"""
find API 原型 v2: 多档并存比价（schema v2 对齐）
查询"白银 价格 采集" → tags 匹配 → 同组聚类 → 排序 → 对比表(含全部档位)
平台成本: 1 次 DB 读缓存 <10ms, 0 LLM 调用（排序分离线预计算）
"""
import json, math, datetime

# ── 模拟 listing 数据（schema v2: price.tiers[] 多档并存）──
LISTINGS = [
    {"id": "npub_a_silver-price-collection", "name": "silver-price-collection", "tags": ["silver", "price", "scraping"],
     "tiers": [
         {"mode": "one_time", "amount": 199, "label": "买断当前版本", "updates": "patch_minor_free"},
         {"mode": "subscription", "amount": 19.9, "period": "monthly", "label": "每月升级订阅", "updates": "all_updates"},
     ], "default_tier": 0, "verify_score": 92, "receipt_fresh_days": 2, "rating": 4.8, "sales": 12, "bid": 0},
    {"id": "npub_b_silver-price-collection-pro", "name": "silver-price-collection-pro", "tags": ["silver", "price", "scraping"],
     "tiers": [
         {"mode": "one_time", "amount": 299, "label": "买断当前版本", "updates": "patch_minor_free"},
         {"mode": "subscription", "amount": 29.9, "period": "monthly", "label": "每月升级订阅", "updates": "all_updates"},
     ], "default_tier": 0, "verify_score": 88, "receipt_fresh_days": 15, "rating": 4.5, "sales": 6, "bid": 5},
    {"id": "npub_c_metals-data-api", "name": "tianji-ge-metals-api", "tags": ["silver", "price", "api"],
     "tiers": [
         {"mode": "subscription", "amount": 49, "period": "monthly", "label": "标准订阅", "updates": "all_updates"},
         {"mode": "one_time", "amount": 499, "label": "终身版", "updates": "all_updates"},
     ], "default_tier": 0, "verify_score": 95, "receipt_fresh_days": 1, "rating": 4.9, "sales": 24, "bid": 0},
    {"id": "npub_d_market-monitor", "name": "market-data-monitor", "tags": ["silver", "market", "monitor"],
     "tiers": [{"mode": "one_time", "amount": 89, "label": "买断", "updates": "current_version_only"}],
     "default_tier": 0, "verify_score": 60, "receipt_fresh_days": 60, "rating": 3.2, "sales": 2, "bid": 0},
    {"id": "npub_e_ctx-framework", "name": "silver-business-context", "tags": ["silver", "analysis", "framework"],
     "tiers": [
         {"mode": "one_time", "amount": 99, "label": "买断", "updates": "current_version_only"},
         {"mode": "rental", "amount": 9.9, "period": "7d", "label": "7天租用", "updates": "current_version_only"},
     ], "default_tier": 0, "verify_score": 75, "receipt_fresh_days": 10, "rating": 4.0, "sales": 8, "bid": 10},
]

SYNONYMS = {
    "白银": ["silver"], "价格": ["price"], "采集": ["scraping", "collect"], "行情": ["market", "price"],
    "api": ["api", "接口"], "监控": ["monitor"], "分析": ["analysis"],
}

def match(query, listing):
    score = 0
    qtags = set(listing["tags"])
    for term in query.split():
        vals = SYNONYMS.get(term, [term.lower()])
        for k in vals:
            if any(k in t or t in k for t in qtags):
                score += 1
    return score

def tier_price(l, mode=None):
    """取档位价: mode 指定则取该档, 否则取 default_tier; 同档位最低价为可比价"""
    tiers = l["tiers"]
    if mode:
        cands = [t for t in tiers if t["mode"] == mode]
        return min(t["amount"] for t in cands) if cands else None
    return tiers[l["default_tier"]]["amount"]

def price_score(l, group, mode=None):
    prices = [tier_price(x, mode) for x in group]
    prices = [p for p in prices if p is not None]
    lo, hi = min(prices), max(prices)
    p = tier_price(l, mode)
    return 1.0 if hi == lo else 1 - (p - lo) / (hi - lo)

def rank(l, group, mode=None):
    ps = price_score(l, group, mode)
    health = 0.5 * (l["verify_score"] / 100)
    fresh = 1.0 if l["receipt_fresh_days"] <= 7 else (0.5 if l["receipt_fresh_days"] <= 30 else 0)
    vs = health + 0.3 * fresh + 0.2 * (l["verify_score"] / 100)  # 0.5×health → health (与文档对齐)
    rs = l["rating"] / 5 if l["rating"] else 0
    vol = math.log10(1 + l["sales"]) / 3 if l["sales"] else 0
    bid = min(l["bid"] * 0.01, 0.1)  # 竞价封顶 0.1
    return 0.35 * ps + 0.25 * vs + 0.20 * rs + 0.20 * vol + bid

print("=" * 96)
print("find API 原型 v2: 查询「白银 价格 采集」 (零 LLM, 多档并存比价, schema v2)")
print("=" * 96)

query = "白银 价格 采集"
matched = [(l, match(query, l)) for l in LISTINGS]
group = [(l, s) for l, s in matched if s >= 2]  # 匹配分≥2 才入比价组
weak = [(l["name"], s) for l, s in matched if s < 2]

print(f"\n[1] tags 匹配分: {[(l['name'], s) for l, s in matched]}")
print(f"[2] 入比价组(分≥2): {[l['name'] for l, _ in group]}  弱相关(仅推荐): {weak}")

# 排序（按 default_tier）→ 输出对比表（含全部档位）
keys = [(rank(x[0], [g[0] for g in group]), x) for x in group]
keys.sort(reverse=True)
group = [x for _, x in keys]
print(f"\n[3] 排序(默认档) → 对比表(全部档位并列):\n")
hdr = f"{'skill':32s} {'默认档':>8s} {'档位列表':<46s} {'验证分':>5s} {'评分':>4s} {'销量':>4s} {'竞价':>4s} {'rank':>6s}"
print(hdr)
print("-" * 96)
for l, _ in group:
    tiers_txt = " | ".join(f"{t['mode']}:${t['amount']}{('/'+t['period']) if t.get('period') else ''}" for t in l["tiers"])
    print(f"{l['name']:32s} ${tier_price(l):>6.0f} {tiers_txt:<46s} {l['verify_score']:>5d} {l['rating']:>4.1f} {l['sales']:>4d} {l['bid']:>4d} {rank(l, [g[0] for g in group]):>6.3f}")

print("\n[4] 按档位单独比价示例 (mode=subscription):")
sub_group = [g[0] for g in group if any(t["mode"] == "subscription" for t in g[0]["tiers"])]
for l in sorted(sub_group, key=lambda x: -rank(x, sub_group, "subscription")):
    amt = tier_price(l, "subscription")
    print(f"  {l['name']:32s} 订阅价 ${amt:>6.1f}/期  rank={rank(l, sub_group, 'subscription'):.3f}")

print("\n[5] 冷启动退化: rating/sales=0 时 rank = 0.35×price + 0.25×verify + bid（验证分主导）")
print("\n平台成本: 1 次 DB 读缓存 <10ms | 0 LLM 调用 | 排序分离线预计算缓存 24h")

# Skill 交易平台 — 定价模式分类体系 v1 (2026-08-24)

四维分类: 使用权模型 × 价格结构 × 计费周期 × 交付权益
一个 tier = 四维各取一值的组合，同一 skill 可挂多 tier（多档并存）。

## 第一维: 使用权模型 (mode) —— 买家获得什么权利

| mode | 定义 | 适合 skill 类型 | 抽佣 | 示例 |
|:--|:--|:--|:--|:--|
| `one_time` 一次性买断 | 付一次 → 永久使用当前版本（patch/minor 免费） | 方法论/知识/流程类（一次性交付） | 15% 一次 | 白银价格 4 层采集方法论 $199 |
| `subscription` 订阅 | 限期内持续使用 + **全部更新** | API/数据/持续维护类（每月新数据源） | 15% 每期循环 | tianji-ge API $49/月 |
| `rental` 租用 | 限时使用权，到期失效 | 短期项目/试用决策 | 15% 每次 | 工具试用 $4.9/7天 |
| `pay_per_use` 按次 | 每次执行/调用/验证收费 | 扫描/查询/生成服务 | 15% 每次 | 深度沙箱检测 $9.9/次 |
| `seat` 席位 | 按使用 agent/用户数收费 | 团队/企业规模化使用 | 15% 每席位每期 | 企业版 $9.9/agent/月 |

## 第二维: 价格结构 (structure) —— 价格如何计算

| structure | 定义 | 落地方式 | 示例 |
|:--|:--|:--|:--|
| `flat` 固定价 | 单一价格 | 一个 tier 条目 | $199 买断 |
| `tiered` 阶梯价 | 功能分层（基础/专业/企业） | **拆成多个 tier 条目**（label 区分, 共用 manifest_hash） | 基础 $49 / 专业 $99 / 企业 $199 |
| `volume` 用量价 | 量越大单价越低 | amount + volume_breakpoints[] | 1-10 次 $9.9/次, 11+ 次 $6.9/次 |
| `dynamic` 动态价 | 随市场供需波动 | 平台建议价区间 + 卖家在区间内调整 | 建议 $149-249, 卖家挂 $199 |

## 第三维: 计费周期 (period) —— 多久收一次钱

| period | 适用 mode | 说明 |
|:--|:--|:--|
| (无) | one_time | 一次性 |
| `monthly` | subscription/seat | 月付（主流, 决策成本低） |
| `quarterly` | subscription | 季付（年费 8.5 折的简化版） |
| `yearly` | subscription | 年付（通常 2 个月折扣, 现金流好） |
| `7d` / `30d` | rental | 租期 |
| `per_use` | pay_per_use | 按次即周期 |

## 第四维: 交付权益 (entitlement) —— 买了之后得到什么

| 权益 | 值 | 说明 |
|:--|:--|:--|
| 版本更新 | `current_version_only` | 只当前版（买断默认） |
| | `patch_minor_free` | patch/minor 免费（买断升级档） |
| | `all_updates` | 全部更新（订阅默认） |
| 技术支持 | `basic` | 30 天 SLA, 48h 响应（默认） |
| | `priority` | 优先支持, 24h 响应, 加价 10-20% |
| 授权范围 | 见 license | private 绑定买家公钥 / single_org 组织域名 / seat 按席位 |

## 组合规则（约束）

1. 每个 tier 必须: mode + structure(默认 flat) + amount + currency
2. mode=subscription/seat → 必填 period（monthly/quarterly/yearly）
3. mode=rental → period 必为 7d/30d
4. mode=one_time → period 省略
5. mode=seat → 必填 seat_price 单位（per_agent/per_user）+ min_seats/max_seats
6. structure=tiered → 建议拆多 tier 条目, 每个 label 注明"基础版/专业版/企业版"
7. structure=volume → amount 为基准价, volume_breakpoints[] 为 [qty, price] 数组
8. 同一 skill 多档并存: 买断+订阅最常见; 订阅档 updates 恒为 all_updates
9. 建议价基准按 mode 分组（见下）

## 平台建议价（按 mode 分组, 冷启动基准）

| mode | 基准区间 | 依据 |
|:--|:--|:--|
| one_time | $29-399（工具→情报） | 价格阶梯: $29-49 入门 / $99-199 主流 / $299+ 高端 |
| subscription | $4.9-99/月 | 持续价值=每月交付, 定价锚=月费感 |
| rental | 买断价的 5-15% | 租用是试错成本 |
| pay_per_use | $0.5-9.9/次 | 按次价值感低, 走量 |
| seat | $2-20/agent/月 | 组织规模化 |

历史成交后: 同 mode 同 tags 前 2 级聚类 → 25-75 分位 = 建议区间; 偏离 >5x 中位标"价格异常"。

## 抽佣汇总表

| mode | 抽佣 | 扣费时点 |
|:--|:--|:--|
| one_time | 15% | 放款时一次 |
| subscription | 15% 每期 | 每期扣费时自动拆账 |
| rental | 15% | 每次租用成交 |
| pay_per_use | 15% | 每次调用结算 |
| seat | 15% 每席位 | 每期随订阅扣 |

订阅循环扣费的安全阀: 扣费失败 2 次 → 降级为无更新版（防沉默扣费投诉）; 退订随时停, 已付周期保留使用权到期末。

## schema 落地（price.tiers 扩展, v3）

```json
{
  "mode": "one_time|subscription|rental|pay_per_use|seat",
  "structure": "flat|tiered|volume|dynamic",
  "period": "monthly|quarterly|yearly|7d|30d|per_use",
  "amount": 199,
  "currency": "usd",
  "label": "买断当前版本",
  "updates": "current_version_only|patch_minor_free|all_updates",
  "support": "basic|priority",
  "seat": {"unit": "per_agent", "min_seats": 1, "max_seats": 100},
  "volume_breakpoints": [[10, 9.9], [50, 6.9]],
  "commission_rate": 0.15
}
```

## 决策规则（买家视角）

```
买家要什么 → 选档
  一次用 → one_time 买断
  持续用+要更新 → subscription
  不确定先试 → rental 试用
  按需高频 → pay_per_use
  团队多人用 → seat
```

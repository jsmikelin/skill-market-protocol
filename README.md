# Skill Market Protocol

去中心化 Skill 交易协议 — 基于 Nostr 事件体系，让 AI Agent 之间可以安全地买卖、对拍验证、交易 skill 包。

## 核心设计

| 层 | 设计 | 说明 |
|:--|:--|:--|
| 身份 | ed25519 密钥对（生产化 secp256k1+BIP340 = NIP-01） | Agent 即身份，无许可参与 |
| 上架 | kind 37001 `skill_listing` | skill 元数据 + price + terms + delivery |
| 回执 | kind 37004 `skill_receipt` | 买家对拍验证回执（verdict/epoch/evidence） |
| 防篡改 | manifest sha256 | 买家拉包重算比对 |
| 支付 | Lightning/Cashu 小额 + 比特币 2-of-3 escrow 大额 + 法币持牌收单 | 平台不经手资金 |

## 交易六步

1. 卖家发布 skill listing（kind 37001）
2. 买家 find 发现（tags 匹配 + 排序分）
3. 付款托管（escrow / 闪电）
4. P2P 拉包验签（sha256 比对）
5. 对拍回执（kind 37004，可执行验收判据）
6. 放款 + 抽佣 15%

## 验收判据（对拍核心）

manifest sha256 只能证明包未被篡改，不能证明功能符合描述。
因此对拍前必须锁定**可执行验收判据文件**（输入样例 + 期望输出 + 判定脚本），
sha256 进 manifest，双方确认后锁版，通过才放款，不通过全额退款。

## 目录

- `protocol/skill_listing.schema.json` — kind 37001 上架事件 JSON Schema v3（多档定价：买断/订阅/租用/按次/席位）
- `tools/package_p0.py` — skill 目录 → zip + sha256 manifest
- `tools/find_skill.py` — find 原型：tags 匹配 + 排序分，零 LLM
- `tools/protocol_loopback.py` — 双 Agent 闭环验证（发布→发现→验签→防篡改→回执，含负面测试）
- `docs/pricing_model_taxonomy.md` — 四维定价分类（mode × structure × period × entitlement）

## 定价模型

抽佣 15%（对标 Agensi 20%、App Store/Steam 30%）。
多档并存：一次性买断 / 订阅（持续升级）/ 限时租用 / 按次 / 席位。

## 状态

实验性协议，闭环验证通过（含负面测试）。生产化待办：
secp256k1+BIP340、真实中继池、托管支付、争议仲裁。

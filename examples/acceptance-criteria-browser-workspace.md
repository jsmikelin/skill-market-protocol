# Example — browser-workspace 验收判据草案

对拍验证的可执行验收判据示例。锁版后 sha256 进 manifest，双方共同确认后不可单方面修改。

## 场景 1: 登录态持久化

- **输入**: 目标站点登录页 URL（测试环境提供）
- **期望输出**: 会话文件生成，重开浏览器后 cookie/profile 复用成功，无需重新扫码
- **判定脚本**: `check_login_persistence.py` — 断言会话文件存在 + 复用后页面出现登录后元素

## 场景 2: 反爬绕过（Cloudflare）

- **输入**: 带 Cloudflare 防护的测试页面 URL
- **期望输出**: HTTP 直连或浏览器降级链任一通道返回 200 + 页面正文非空
- **判定脚本**: `check_cf_bypass.py` — 断言状态码 200 且正文长度 > 500 字符

## 场景 3: 结构化抽取

- **输入**: 目标页面 URL + 抽取 schema（字段定义）
- **期望输出**: JSON 数据符合 schema，字段非空
- **判定脚本**: `check_extract.py` — 断言 JSON 结构 + 非空字段

## 判定脚本约定

- 判定脚本为纯 Python 单文件，无第三方依赖（标准库即可）
- 退出码 0 = 通过；非 0 = 不通过
- 输出 `PASS` / `FAIL + 原因` 到 stdout，作为回执 evidence

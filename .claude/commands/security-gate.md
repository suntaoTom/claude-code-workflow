---
description: 安全门禁 — review 与 build 之间, 对当前分支 pending 改动跑内置 /security-review + 前端泄密红线, 命中 🔴 阻塞构建
argument-hint: [--base <分支, 默认 main>]
allowed-tools: Bash, Read, Grep, Glob, Skill, Agent
idx: 6
---

你现在是**安全门禁 (security gate)** 角色。位置: 主流程 `review` 之后、`build` 之前的**硬门禁**。
职责单一 —— 只看本次改动有没有踩**前端泄密/安全红线**, 有就**拦住, 不许进 build**。

## 为什么单独有这一道 (不和 /review 合并)

`/review` 是全维度找问题 (性能/规范/测试/安全…), 范围是你指定的文件或目录。
本门禁不同, 三个特征决定它必须独立:

1. **只看本次 diff** — 扫「当前分支相对 base 的 pending 改动」, 不全量审。发版前最后一道, 关心的是「这批要上线的改动有没有引入泄密」。
2. **只盯安全红线** — token/密钥/XSS 这条线, 前端应用的命门。`/review` 顺带扫安全, 但顺带 ≠ 专门; 发版门禁值得一道**专扫**。
3. **卡 build** — 命中 🔴 直接阻塞流程, 不是「报告完由人决定」。

> 红线明细的**单一来源**是 [review.md 维度 2 安全](review.md) + [no-hardcode.md](../rules/no-hardcode.md), 本文件不重写细则, 只负责「圈定 diff 范围 + 跑扫描 + 卡门」。

## 扫描范围

```bash
BASE="${1:-main}"   # --base 指定, 默认 main
# 本次改动涉及的前端源文件 + 配置 (已提交 + 工作区未提交)
git diff --name-only "$BASE"...HEAD -- 'workspace/src/**/*.{ts,tsx}' 'workspace/config/**' 'workspace/.env*'
git diff --name-only -- 'workspace/src/**/*.{ts,tsx}' 'workspace/config/**'   # 未 commit 的
```

只对**这批变更文件**做安全扫描。无相关改动时直接放行 (输出「本次无前端源码/配置改动, 安全门禁跳过」)。

## 执行流程

### 第一步: 跑内置基线扫描

调用内置 `/security-review` skill (Claude Code 自带的「当前分支 pending 改动安全审查」引擎) 拿通用安全基线 (注入/越权/密钥处理/不安全依赖等)。

### 第二步: 叠加前端专属红线 (命中任一即 🔴 Critical, 阻塞)

对第一步圈定的变更文件, 逐条扫前端泄密/安全红线:

- **密钥 / token / password / 私密 appSecret** 硬编码在源码, 或提交进 `config/` / `.env*` (前端 bundle 用户可读, 等于公开)
- **XSS**: `dangerouslySetInnerHTML` 使用未消毒的用户输入 / 接口返回拼接 HTML
- **`eval` / `new Function` / 动态 `import()` 执行不可信字符串**
- 敏感信息 (token/手机号/身份证等 PII) 进 `console.log` / 上报到第三方埋点
- 未转义用户输入拼接 URL / 跳转 (开放重定向) / `window.location` 注入
- 引入**不可信来源的第三方脚本** (`<script src>` 指向非自有 CDN) 或内联远程脚本
- 关闭了框架默认的安全防护 (如手动 `rel` 去掉 `noopener` 的 `target=_blank`)

**grep 起手式** (在变更文件上扫, 不是全仓):

```bash
# 密钥/token 硬编码线索
grep -nE '(secret|token|apikey|api_key|password|appSecret|private[_-]?key)\s*[:=]' <变更文件>
# XSS / 动态执行
grep -nE 'dangerouslySetInnerHTML|eval\(|new Function\(' <变更文件>
# 敏感信息进日志
grep -nE 'console\.(log|info|warn|error)' <变更文件> | grep -iE 'token|password|secret|phone|idcard'
```

> grep 只是定位线索, **最终判定靠读上下文** —— 命中不等于违规 (例: 变量名含 token 但来自后端 set-cookie 不落前端), 漏 grep 也不等于安全 (语义级泄露 grep 抓不到)。变更面大时可 spawn `Agent` 按文件并行扫 (见 [concurrency.md](../rules/concurrency.md)), 红线判定回主 agent 收口。

### 第三步: 门禁判定

- **任一 🔴** → **阻塞**。明确列出: 文件:行号 + 违反的红线 + 修复方向。**不得进入 `build`**。让用户走 `/fix` 修完重跑本门禁。
- **0 🔴** → 放行, 可进 `/build`。🟡 / 🔵 安全建议照列, 但不阻塞 (由用户决定)。

## 输出 (持久化, 同 /test 报告惯例)

写报告到 `docs/reports/security/security-gate-<YYYY-MM-DD>.md` (目录不存在先建, 同日覆盖):

```markdown
# 安全门禁报告

| 项 | 值 |
|---|---|
| 日期 | YYYY-MM-DD |
| base 分支 | main |
| 当前分支 | <branch> |
| 变更前端文件数 | N |
| 内置 /security-review | 通过 / 发现 N 项 |
| 前端红线 🔴 | N |
| 门禁结论 | ✅ 放行 / 🔴 阻塞 |

## 1. 🔴 阻塞项 (必须修)
<文件:行号 + 红线 + 修复方向; 无则写「无」>

## 2. 🟡 / 🔵 安全建议 (不阻塞)

## 3. 扫描范围 (变更文件清单)

## 4. 重现命令
```

最终汇报: 门禁结论 (放行 / 阻塞) + 报告路径 + 若阻塞列出必修项。

请对当前分支执行安全门禁:
$ARGUMENTS

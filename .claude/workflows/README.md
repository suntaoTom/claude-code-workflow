# Workflow 编排脚本

> `Workflow` 工具的命名脚本目录。把 [concurrency.md](../rules/concurrency.md) 的「拓扑分层 → 层内并行 → 共享文件主 agent 收口」从**文字规则**落成**可执行的确定性编排**。

## 这是什么 / 不是什么

- **是**: 多 agent 并行编排的脚本 (JS)。`Workflow({scriptPath})` 调用。fan-out 子 agent、流水线、对抗式复核等都在脚本里写死, 可缓存可 resume。
- **不是**: `.claude/commands/*.md` 那种命令定义, 也不是 `workflow.json` 那个命令拓扑图。三者别混:
  | 文件 | 角色 |
  |------|------|
  | `.claude/commands/*.md` | 命令的 prompt 定义 (主 agent 读) |
  | `.claude/workflow.json` | 命令之间的执行**顺序**拓扑 (prd→plan→code…) |
  | `.claude/workflows/*.js` | 单个命令内部的**多 agent 并行编排**脚本 (本目录) |

## ⚠️ 计费 + 显式 opt-in

`Workflow` 会并发起多个子 agent, **token 成本是普通一次回答的数倍**, 且**默认锁定** —
只有用户明确要 (「用 workflow 跑 /review」「ultracode」「并行审查」) 时才允许调用。
平时小范围任务**沿用命令的默认串行流程**, 不值得起 Workflow。

## 脚本清单

| 脚本 | 对应命令 | 职责 | 入参 (args) | 产出 |
|------|---------|------|------------|------|
| `review.js` | `/review` | 按文件 fan-out `code-reviewer` 并行审查 (7 维度) → 对每条 Critical 对抗式复核滤误报 → 汇总 (只读不改码) | `{ files: string[], target: string }` | `{ counts, critical[], warning[], suggestion[] }` |

### review.js 约定

- **文件发现 (Glob) 在调用前由主 agent 完成**, 脚本只接收清单 → 保持纯读、无 fs 依赖, 契合「共享文件主 agent 收口」。
- **必须用 `scriptPath: ".claude/workflows/review.js"` 调用, 不要用 `name: "review"`**: named workflow 注册会被缓存、不热重载, 改了脚本用 name 调还是跑旧快照。`scriptPath` 每次读最新源文件。
- 脚本**只产报告数据, 不改代码**。修复循环 (写文件 / 同步 README / 补测试) 由主 agent 串行收口, 见 [review.md「并行编排模式」](../commands/review.md)。
- 安全/泄密红线 (token/密钥写前端、XSS) 与 i18n 硬编码的 Critical 复核**从严**: 不确定一律保留。

## 新增脚本时

1. 文件名 = 对应命令名 (`<command>.js`)。
2. 顶部 `export const meta = {...}` 必须是纯字面量 (不能用变量/函数)。
3. 入参走 `args` (JSON 值); 脚本应容错「对象 or JSON 字符串」两种 (某些 harness 会序列化)。
4. 写文件类的「收口」步骤交主 agent, 脚本尽量保持只读或仅各写各的源文件。
5. 在本表登记一行。

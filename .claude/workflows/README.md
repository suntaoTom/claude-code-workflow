# Workflow 编排脚本

> `.claude/workflows/*.js` 是命令内部的多 agent 编排脚本；`.claude/workflow.json` 是命令之间的 SDLC 顺序拓扑。

## 计费与 opt-in

只有用户明确要求并行审查/Workflow/ultracode 时才运行；小范围任务沿用命令默认流程。所有脚本必须让共享文件由主 agent 串行收口。

## 脚本清单

| 脚本 | 对应命令 | 职责 | 入参 | 产出 |
|------|---------|------|------|------|
| `review.js` | `/review` | 按 Java/POM/配置文件 fan-out 审查分层、可靠性、安全和追溯，对 Critical 复核并汇总 | `{ files: string[], target: string }` | `{ counts, critical[], warning[], suggestion[] }` |

## review.js 约定

- 文件发现由命令层 Glob 完成，脚本只接收清单。
- 用 `scriptPath: ".claude/workflows/review.js"` 读取最新脚本。
- 脚本只产报告数据，不改源码；修复由主 agent 走 `/fix`。
- 安全、消息丢失、未授权和凭据问题不因不确定而自动丢弃。

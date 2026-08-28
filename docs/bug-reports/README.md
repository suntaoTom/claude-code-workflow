# bug-reports/ — Java 后端故障报告

> 这是测试、监控或人工故障输入与 `/fix` 之间的数据契约。报告必须脱敏、可复现、可追溯。

## 文件清单

| 文件 | 作用 |
|------|------|
| `_template.md` | Bug 报告固定字段 |
| `<YYYY-MM-DD>-<module>.md` | 一轮故障报告，可含多个 Bug |

## 必填证据

Bug ID、P0/P1/P2、服务/模块、版本/profile/环境、现象、前置和步骤、期望/实际、关联 PRD/task/rules。HTTP/WebSocket/RabbitMQ/事务问题另填 traceId、requestId、messageId、correlationId、消息类型、exchange/queue/routing key、Inbox/Outbox/DLQ 和事务状态（均脱敏）。

## 流程

```text
报告 → /bug-check 分诊与校验 → 人工 review → /fix 失败测试 + 最小修复 → /test 回归 → PR/MR
```

`true-bug` 才进入 `/fix`；feature 或 PRD 漏规则回到 `/prd`。报告不写修复代码建议，不粘贴 Token、密码、Cookie、连接串、PII 或完整业务 Payload。

## 与测试报告的关系

- `bug-reports/`：描述需要修复的运行态故障，流向 `/fix`。
- `test-reports/`：记录自动化验证结果、规则覆盖和未执行边界，供 review/复盘。

两者都只追加，不修改既有快照。

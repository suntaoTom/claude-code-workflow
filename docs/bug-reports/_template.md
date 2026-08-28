# Java 后端故障报告：<模块>

> 这是 `/bug-check` 的机器可读入口。不得写入 Token、密码、Cookie、连接串、PII 或完整敏感 Payload。

## 元信息

| 项 | 值 |
|----|----|
| 报告 ID | `YYYY-MM-DD-<module>` |
| Bug ID | `B001` |
| 优先级 | P0 / P1 / P2 |
| 服务/模块 | |
| 版本 / commit / profile | |
| 环境 / 实例 | |
| 触发人 | |
| 关联 PRD/task/rules | |

## 运行上下文

| 字段 | 值 |
|------|----|
| traceId / requestId | 脱敏值 |
| messageId / idempotency key | 脱敏值或无 |
| correlationId | 脱敏值或无 |
| API / WebSocket 消息类型 | |
| Rabbit exchange/queue/routing key | |
| Inbox/Outbox/DLQ 状态、重试次数 | |
| 数据库事务状态 | |

## 分诊

- 分类：`true-bug` / `missing-rule` / `feature` / `ambiguous`
- 分类依据：真实 PRD/@rules 锚点

## 现象与复现

- 前置条件：
- 步骤：
  1.
- 期望：
- 实际：

## 脱敏日志与证据

```text
仅粘贴已脱敏的异常类型、错误码、traceId 和必要堆栈；不要粘贴凭据或完整消息体。
```

## 根因推测（可选）

> 只写线索，不写修复代码建议；由 `/fix` 验证。

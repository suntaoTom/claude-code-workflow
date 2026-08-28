# PRD 后端人工审阅指南

## 通过标准

`[待确认]` 必须为零；`[默认假设]` 需在审阅时确认或升级为正式规则。每条业务规则必须可转为 JUnit、集成测试或明确的人工步骤。

## 后端重点

- 调用边界：HTTP、原生 WebSocket（非 STOMP/SockJS）还是 RabbitMQ；调用方和权限是否明确。
- 协议契约：字段、版本、错误码/关闭码、messageId/idempotency/correlationId 是否有真实来源。
- 可靠性：事务、Inbox/Outbox、ack、重试上限、退避、DLQ、重复投递和消息转换失败是否明确。
- WebSocket：握手身份、Origin、连接/消息限制、Ping/Pong、超时、关闭和多实例策略。
- 运行：Nacos/profile、Redis、数据库、Actuator、指标、trace、SLA、告警和回滚。
- 安全：不在 PRD 写真实凭据、Token、连接串、PII 或完整 Payload。

## 上游忠实性

引用必须是真实路径和锚点；“与产品确认/评审通过”必须有变更记录、commit/MR 证据。产品文档、协议和参考实现冲突时，增加 `## 冲突待决` 并停止下游，不自行拍板。

## 验证

```text
/prd-check @docs/prds/<module>.md
```

只有检查通过才执行 `/plan`。不确定的内容应改为范围外、待评审建议或回到上游补充，而不是猜一个实现。

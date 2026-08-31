# 上游文档忠实性（Upstream Fidelity）

> 产品需求、API/WebSocket/RabbitMQ 契约、架构文档和迁移说明是下游产出的单一事实源。PRD、task、Java 代码、测试和部署配置必须遵循上游意图，不允许 AI 自行联想、重构或覆盖。

## 适用范围

| 上游 | 下游 | 主要阶段 |
|------|------|----------|
| 产品/业务需求（含导入原文） | Java 后端能力需求书 | `/prd`、`/prd-check` |
| OpenAPI JSON | Controller、DTO/VO、契约测试和接口索引 | `/plan`、`/code`、`/test`、`/review` |
| WebSocket schema | Handler、消息校验和 WebSocket 测试 | `/plan`、`/code`、`/test` |
| RabbitMQ 消息契约/拓扑 | Producer/Consumer、Inbox/Outbox、重试/DLQ | `/plan`、`/code`、`/review` |
| 架构/迁移文档 | 分层、事务、兼容和部署策略 | 全流程 |

## 硬规则

### R1：引用必须真实

引用必须包含真实文件路径、行号、锚点或协议标识。写入前先读取/检索上游文件；不存在的 operationId、消息类型、配置键、表或章节不得作为依据。

### R2：不改写上下文

不得把一个接口、消息、消费者、队列或事务边界的语义套到另一个上下文；不得凭空添加字段、错误码、路由、重试、权限或部署行为。行业惯例只能作为待评审建议。

### R3：评审结论必须有证据

不得凭空写“与产品确认”“已评审通过”“架构决定”。证据只能来自 PRD 变更记录、commit/MR/PR approval 或明确的用户决策。无证据时写“待评审”或“待用户确认”。

### R4：冲突必须阻塞

当产品需求、协议、架构、旧实现或部署约束冲突时，在 PRD 增加 `## 冲突待决`，列出冲突原文和候选方案；`/prd-check`/`/plan-check` 阻塞，等待用户选择，不自行拍板。

### R5：参考项目不是当前事实

`/Users/sundaotao/Desktop/web3/backend/microboot-service-websocket` 只作为 Java 技术背景。除非用户明确提供并确认引用，不能把其业务 Payload、Secret、部署地址、父 POM 实际解析版本或私有依赖行为写成当前目标项目事实。

## 检查清单

- [ ] PRD、task、JavaDoc 和测试中的 `@prd/@task/@api/@rules` 指向真实内容。
- [ ] API、WebSocket、RabbitMQ、数据库 migration 和配置引用有唯一事实源。
- [ ] “已确认/评审通过”有变更记录或 MR/PR 证据。
- [ ] `## 冲突待决` 存在时没有进入 `/plan`。
- [ ] 未把“业界惯例/这样更好”写成已定业务规则。
- [ ] 下游新增内容可反向追溯；无法追溯时标待评审并停止。

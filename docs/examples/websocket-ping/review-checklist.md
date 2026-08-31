# Review Checklist — WebSocket Ping/Pong

- [ ] 使用原生 Spring WebSocket `TextWebSocketHandler`，没有无需求引入 STOMP/SockJS。
- [ ] 握手身份和用户类型在业务处理前校验。
- [ ] Origin、消息大小、频率、心跳、超时和连接上限来自配置。
- [ ] ping/pong 不进入业务消息路由，业务 Payload 不被传输层改写。
- [ ] Session 注册和关闭幂等，异常路径释放资源。
- [ ] JavaDoc 含真实 `@prd/@task/@api/@rules`，目录 README 已更新。
- [ ] JUnit 覆盖每条可自动化规则；未执行项标为 NOT_RUN/MANUAL。
- [ ] 未打印 Token、密码、Cookie、PII 或完整消息 Payload。
- [ ] 多实例路由限制和部署前提已在 PRD/ADR 中明确。

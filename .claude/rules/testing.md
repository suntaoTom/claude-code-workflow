# Java 后端测试规范

## 测试断言唯一来源

业务断言唯一来源是生产 JavaDoc 的 `@rules`，并与 PRD 原文和 task `businessRules` 对照。每条 `@rules` 一个独立测试用例，测试名称完整引用规则原文和编号；不得根据源码现状猜预期。

## 测试分层

| 场景 | 工具/位置 |
|------|-----------|
| 纯函数、转换、校验 | JUnit 5 + Mockito/AssertJ，镜像 `src/main/java` 包路径 |
| Controller/HTTP | Spring Boot slice / MockMvc（仅当服务有 HTTP API） |
| Service/事务 | Spring Boot Test 或隔离单测，验证提交/回滚语义 |
| DAO/MyBatis-Plus | 数据库集成测试，验证查询、唯一约束、迁移和并发边界 |
| Redis | 隔离 Redis 集成测试，验证 TTL、Presence、锁和失效 |
| RabbitMQ | 拓扑、Confirm/Return、Inbox/Outbox、ack、重试、DLQ 集成测试 |
| WebSocket | Spring Mock WebSocket/真实测试容器，验证握手、消息、心跳、关闭和资源释放 |
| 契约 | OpenAPI 或 WebSocket/Rabbit 消息 schema 一致性检查 |

测试目录固定为 `workspace/src/test/java/<base-package>/`，按生产包镜像；测试资源放 `workspace/src/test/resources/`。不创建前端 `workspace/tests`、Vitest、Playwright 或 Testing Library 目录。

## WebSocket 必测规则

根据 PRD/协议实际规则覆盖：身份缺失/无效、用户类型、Origin、连接数、消息大小/频率、Ping/Pong、超时、正常/异常关闭、重复 messageId、显式入站路由和未登记消息处理。不能把跨浏览器、真实网络抖动、负载下吞吐、多节点连接迁移伪装成普通单测。

## RabbitMQ 必测规则

覆盖 messageId/idempotency key/correlationId 语义、Inbox 状态、Outbox 事务关系、Confirm/Return、ack 时机、有限重试、退避、DLQ、消息转换 fatal、旧新契约兼容。真实生产 Broker 故障切换和灾备属于人工/专项环境。

## 测试失败分诊

1. 测试代码错误（fixture、selector、异步等待、测试隔离）→ 修测试。
2. 环境缺失（JDK、Maven、数据库、Redis、RabbitMQ、Nacos）→ 报告环境，不擅自伪造通过。
3. 预期与 PRD/@rules 不一致 → 按原文修正测试或请求规则确认。
4. 源码违反明确规则 → 走 `/fix`，不要在 `/test` 中改生产源码。

## 自动化边界与停止标准

🟢 自动化：业务逻辑、DTO 转换、参数校验、错误映射、事务、WebSocket 握手/消息、Rabbit 治理、Redis 状态和配置绑定。

🔴 转人工或专项环境：真实生产依赖、生产发布/回滚、真实灾备、跨节点 WebSocket 会话、真实负载/网络故障、证书轮换、云网关超时和第三方身份服务。

达到以下全部条件即停止新增自动化：所有可自动化 `@rules` 100% 覆盖；WebSocket/RabbitMQ/数据库关键规则至少有对应集成测试；完整 Maven 测试连续两轮通过；不可自动化规则已进入 `docs/test-reports/manual-checklist-YYYY-MM-DD.md`。

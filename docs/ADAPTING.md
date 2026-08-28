# 跨工种适配：Java 后端基线

本仓库保留跨工种 SDLC 内核，但当前领域已切换为 Java 后端。参考项目 `/Users/sundaotao/Desktop/web3/backend/microboot-service-websocket` 只提供技术背景，不复制源码、不绑定 workspace。

## 保留的内核

- `prd → plan → code → test → review → build → deploy → release` 骨架和检查门禁
- PRD → task → 产出物 `@prd/@task/@api/@rules` → 测试的追溯链
- 任务状态机、人工审批、失败显式化、ADR、测试报告、元审计
- 无依赖且不写同一文件时并行，README/配置/协议/status 串行收口

## 当前 Java 领域层

| 文件 | Java 后端职责 |
|------|---------------|
| `tech-stack.md` | Java 21、Maven、Spring Boot/Cloud/Alibaba、Nacos、原生 WebSocket、RabbitMQ、Redis、MyBatis-Plus、Actuator |
| `coding-style.md` | Alibaba Java Guidelines、分层、构造器注入、DTO/Form/BO/DO/VO、事务、日志 |
| `no-hardcode.md` | Secret、连接串、阈值、队列、错误码和可变运行配置外置 |
| `file-docs.md` | JavaDoc、package-info、README 和追溯锚点 |
| `testing.md` | JUnit/Spring/消息/数据库/WebSocket/契约测试及人工边界 |
| `reliability.md` | Inbox/Outbox、ack、幂等、重试、DLQ、事务和连接生命周期 |
| `security.md` | WebSocket/Rabbit/配置/日志/Actuator/SQL/容器安全 |

## Java 任务映射

```text
contract → schema/config/migration → domain/dao → service
→ controller/websocket/messaging → unit/integration/contract-test
→ docker/ci/deploy/runbook
```

不同模块可并行；共享 Maven 配置、协议、迁移和 README 必须主 agent 收口。

## 技术事实与待确认

参考项目已核实 Java 21、Maven 3.9.9、Spring Boot 3.2.12、Spring Cloud 2023.0.6、Spring Cloud Alibaba 2023.0.3.4、Nacos、原生 `/ws`、RabbitMQ、Redis、MyBatis-Plus、Actuator、Micrometer、OpenTelemetry、JUnit 和 GitLab Java GitOps。参考项目 POM 与 README 的 `micro-parent` 版本范围冲突，实际版本必须通过 effective POM 冻结。

当前工作流不创建示例服务。未来接入具体 Java 工程时，还必须确认 package/groupId、业务契约、父 POM、Nacos 配置、认证、部署目标、集成测试依赖和多副本路由策略；未确认事项不能由 AI 自行拍板。

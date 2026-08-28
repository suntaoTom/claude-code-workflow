# Java 后端技术栈与工程约定

## 技术基线

以参考项目 `microboot-service-websocket` 已核实的公开工程事实为默认背景；具体业务服务仍以自身 POM、协议和 ADR 为准：

- Java 21、Maven 3.9.9
- Spring Boot 3.2.12、Spring Cloud 2023.0.6、Spring Cloud Alibaba 2023.0.3.4
- Nacos Config/Discovery、Spring Cloud LoadBalancer
- Spring 原生 WebSocket：`@EnableWebSocket`、`TextWebSocketHandler`，非 STOMP/SockJS；参考握手路径 `/ws`
- Spring AMQP/RabbitMQ：Publisher Confirm/Return、Inbox/Outbox、Retry、DLQ/DLX
- Redis `StringRedisTemplate`；MyBatis-Plus；Flyway 能力以公共 starter/服务配置为准
- Spring Boot Actuator、Micrometer、OpenTelemetry
- JUnit 5、Mockito、AssertJ、Spring Boot Test；Spotless
- Docker 分层 Spring Boot Jar、Liberica JDK 21；GitLab CI + GitHub Actions 双入口可用

参考项目 `pom.xml:6` 的 `micro-parent` 为 `[2.1.0,2.2.0)`，但 `README.md:22` 为 `[2.0.0,2.1.0)`；父 POM 的实际解析版本必须通过 `mvn help:effective-pom` 验证，不能猜测。

## Maven 标准结构

```text
workspace/
├── pom.xml
├── src/main/java/<base-package>/
│   ├── Application.java
│   ├── controller/       # HTTP 入口（如有）
│   ├── service/          # 业务编排和事务边界
│   ├── dao/              # 持久化访问
│   ├── domain/           # dto/form/bo/do/vo 与领域规则
│   ├── infra/            # websocket/messaging/cache/persistence/observability 适配
│   └── config/           # Spring 配置和 Properties 绑定
├── src/main/resources/
│   ├── application.yml
│   └── application-<profile>.yml
├── src/test/java/<base-package>/
├── src/test/resources/
├── Dockerfile
└── docs/
```

测试包镜像生产包：`controller/`、`service/`、`dao/`、`infra/websocket/`、`infra/messaging/`、`contract/`、`integration/`。

## 依赖方向

```text
controller / websocket handler → service → dao
                         ↘ infra adapters
```

- Controller/Handler 不直接访问 DAO。
- Service 负责业务编排、事务边界和领域错误映射。
- DAO 只负责持久化；Infra 负责 WebSocket、RabbitMQ、Redis、外部系统和可观测性适配。
- DTO/Form/BO/DO/VO 不混用；DO 不直接作为对外响应。
- 配置从 Spring `@ConfigurationProperties`、profile、Nacos 或 Secret 读取。

## 本地依赖与运行验证

参考项目的本地集成依赖为 Nacos、RabbitMQ、MariaDB、Redis；是否由目标工程的 Compose、CI 模板或外部环境提供，必须在 PRD/任务中明确。默认验证顺序：

```bash
mvn -B -ntp validate
mvn -B -ntp spotless:check
mvn -B -ntp test
mvn -B -ntp verify
```

服务接入后再验证 `/actuator/health`、readiness、WebSocket `/ws` 和消息链路。未启动真实依赖时不得把集成测试写成通过。

## 不在本规则中假设的内容

- 不默认引入 JPA、Springdoc、STOMP、SockJS、Kafka、Testcontainers 或 Kubernetes。
- 不默认存在 REST/OpenAPI；WebSocket JSON 与 RabbitMQ 消息契约必须指向真实协议文件。
- 不默认多副本无状态：参考项目的临时 RPC 回复路由在本机内存，需单实例或粘性路由，除非 ADR 明确改变。

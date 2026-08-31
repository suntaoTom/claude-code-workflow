# 项目配置 - AI Java 后端自动化工作流

> Claude Code 入职培训。详细规则拆分在 `.claude/rules/` 下，按需读取；先确认上游 PRD、协议和部署约束，再执行对应命令。

## 项目定位

本仓库维护的是一套**面向 Java 后端团队的 SDLC 工作流**，不是业务服务源码。参考项目 `/Users/sundaotao/Desktop/web3/backend/microboot-service-websocket` 仅作为技术背景，不是本仓库依赖，不复制源码、不建立 submodule/软链接、不绑定为 `workspace/`。

| 层级 | 目录 | 职责 |
|------|------|------|
| 框架层 | `.claude/` / `docs/` / `CLAUDE.md` | 命令、规则、代理、hooks、PRD、任务与验证报告 |
| 目标工程 | `workspace/` | 用户后续接入的 Java/Maven 服务；本次不生成示例服务 |

## P0 配置与安全边界

所有会随环境、租户、部署或协议变化的值必须通过 Spring 配置、环境变量、Secret、集中常量或协议契约提供，禁止硬编码。密码、Token、私钥、连接串、完整业务 Payload 和 PII 不得进入源码、日志、测试 fixture、PRD 或提交内容。

详见 `.claude/rules/no-hardcode.md`、`.claude/rules/security.md` 与 `.claude/rules/reliability.md`。

## 技术栈基线

以参考 WebSocket 服务核实的技术背景为默认语境：

- Java 21；Maven 3.9.9；Spring Boot 3.2.12
- Spring Cloud 2023.0.6；Spring Cloud Alibaba 2023.0.3.4
- Nacos Config/Discovery；Spring Cloud LoadBalancer
- 原生 Spring WebSocket：`@EnableWebSocket` + `TextWebSocketHandler`，非 STOMP/SockJS
- Spring AMQP + RabbitMQ；Publisher Confirm/Return；Inbox/Outbox、重试与 DLQ
- Redis `StringRedisTemplate`；MyBatis-Plus；Actuator；Micrometer；OpenTelemetry
- JUnit 5、Mockito、AssertJ、Spring Boot Test；Spotless；Docker 分层 Spring Boot Jar；Liberica JDK 21
- CI 默认同时支持 GitLab CI（参考项目使用共享 Java GitOps 模板）和 GitHub Actions；同一环境只能有一个部署入口生效

参考项目的 `pom.xml:6` 与 `README.md:22` 对 `micro-parent` 版本范围存在冲突；除非用户确认并完成 effective POM 验证，任何文档都只能标记为待确认。

## 编码概要

- 遵循 Alibaba Java Coding Guidelines；类/接口/枚举 UpperCamelCase，方法/变量 lowerCamelCase，常量 UPPER_SNAKE_CASE
- 构造器注入；Controller、Service、DAO、Infra 职责清晰，依赖方向单向
- DTO/Form/BO/DO/VO 按边界使用；外部 DTO 不直接映射数据库 DO，DO 不直接作为 API VO
- 配置使用 `@ConfigurationProperties`/Spring profile/外部配置；不在业务代码硬编码环境值
- 异常保留 cause；日志使用 SLF4J 参数占位符并脱敏；不使用 `System.out`/`printStackTrace`
- 每个 Java 源文件必须有 JavaDoc 追溯锚点；每次修改代码同步维护目录 README
- Git 提交格式沿用 `type(scope): description`；保护分支通过 MR/PR 合并

详见 `.claude/rules/coding-style.md`、`.claude/rules/file-docs.md`。

## 测试概要

- 业务断言唯一来源是源文件 JavaDoc 的 `@rules`，每条规则对应独立测试用例
- 单元测试优先；需要 Spring 容器、数据库、Redis、RabbitMQ 或 WebSocket 时使用对应集成测试
- 测试目录按生产包镜像：`workspace/src/test/java/<base-package>/`
- 不伪造真实生产基础设施、负载、多节点故障、跨网络行为或生产发布结果；不可自动化事项写入人工 checklist
- 测试失败按“测试代码 → 环境 → 预期 → 源码”分诊，源码是最后才怀疑的对象
- 所有 Maven 操作优先通过 `./tools/backend.sh`，脚本固定指向 `workspace/pom.xml`；不要在根目录执行裸 `mvn`

详见 `.claude/rules/testing.md`。

## 工作流拓扑

`.claude/workflow.json` 定义唯一拓扑：

`/prd → /prd-check → /plan → /plan-check → /code → /test → /review → /security-gate → /build → /deploy → /release`

Bug 支流：`/bug-check → /fix → /test`。独立工具：`/start`、`/meta-audit`。

`gate` 不通过不能进入下一步；任务状态为 `pending → in-progress → done/blocked`；共享 README、配置、协议、任务状态和 CI 入口由主 agent 串行收口。

## 目录约定

目标 Java 工程接入后采用 Maven 标准布局：

```text
workspace/
├── pom.xml
├── src/main/java/<base-package>/
│   ├── controller/ service/ dao/ domain/ infra/ config/
│   └── package-info.java
├── src/main/resources/
│   ├── application.yml
│   └── application-<profile>.yml
├── src/test/java/<base-package>/
├── src/test/resources/
├── Dockerfile
└── docs/
```

本仓库当前不假设 `workspace/` 已是可运行服务；不得因缺少业务需求而自行创建 Java 生产代码。

## 文档与追溯

- `.workflow-manifest.yml`：母版领域、workspace 路径、活跃输入和安装策略
- `docs/backend-project-profile.yml`：目标后端项目的版本、能力、契约、CI 和部署适配
- `docs/prds/`：后端能力/API/消息需求书
- `docs/tasks/`：`/plan` 生成的任务清单
- `docs/bug-reports/`：规范化缺陷报告
- `docs/test-reports/`：自动化结果与人工 checklist
- `docs/retrospectives/`：不可变元审计报告
- `docs/DECISIONS.md`：架构与流程 ADR

每个产出物通过 `@prd`、`@task`、`@api`、`@rules` 形成需求 → 任务 → Java 代码 → 测试的可追溯链。

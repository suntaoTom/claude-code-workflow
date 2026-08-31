# Java 后端自动化工作流

> 运行在 Claude Code 之上的 Java 后端 SDLC 工作流框架：把需求、协议、实现、验证、安全、构建、部署和发布串成可追溯链。

## 定位

本仓库维护工作流配置和文档，不是业务服务源码。技术背景参考 `/Users/sundaotao/Desktop/web3/backend/microboot-service-websocket`：Java 21、Maven、Spring Boot、原生 WebSocket、RabbitMQ、Redis、MyBatis-Plus、Actuator、JUnit 和 GitLab Java GitOps。参考目录不被复制、引用或绑定。

## 母版目录边界

```text
根目录：AI 工作流层（.claude/、CLAUDE.md、docs/、tools/）
workspace/：后端工程层（pom.xml、src/、resources、tests、Dockerfile）
.github/ 与 .gitlab-ci.yml：宿主平台集成层，不放业务 Java 源码
```

`workspace/` 是后端项目唯一容器。母版不包含业务 Java 代码；复制到具体项目后，将 Maven/Spring 服务放入 `workspace/`，填写 [backend-project-profile.yml](docs/backend-project-profile.yml)，从仓库根目录启动 Claude Code。

初始化或更新可使用：

```bash
./tools/install-java-backend-workflow.sh /path/to/target-repository --dry-run
./tools/install-java-backend-workflow.sh /path/to/target-repository
./tools/backend.sh validate
```

安装脚本默认不覆盖目标已有代码、POM、文档、CI 或部署配置；CI 模板需显式使用 `--with-ci`。完整边界见 [workspace/README.md](workspace/README.md)。


辅助命令：`/bug-check`、`/fix`、`/start`、`/meta-audit`。

| 阶段 | Java 后端产出 |
|------|---------------|
| `/prd` | API、WebSocket 或异步消息需求书 |
| `/plan` | contract/schema/config/controller/service/dao/infra/test 任务清单 |
| `/code` | Maven 标准布局下的 Java、配置、迁移和消息基础设施 |
| `/test` | JUnit、Spring Boot、数据库/Redis/RabbitMQ/WebSocket/契约测试 |
| `/review` | 分层、事务、可靠性、协议兼容、性能和安全审查 |
| `/build` | JAR、Docker 镜像、测试报告、SBOM/校验信息 |
| `/deploy` | GitLab 或 GitHub 目标环境部署、健康检查、`/ws` smoke test |
| `/release` | artifact/镜像/迁移/协议版本、兼容性和回滚记录 |

## 核心原则

1. **可追溯**：PRD 锚点 → task ID → JavaDoc `@prd/@task/@api/@rules` → 测试用例。
2. **人监督关键节点**：需求、任务、代码审查和生产部署必须有人确认。
3. **失败显式可见**：不跳过错误；真实生产基础设施、多节点、负载和故障演练不伪装成自动化通过。
4. **可靠性优先**：WebSocket 身份和生命周期、RabbitMQ ack/幂等/重试/DLQ、Redis Presence、事务边界和协议兼容必须有来源。

## 技术背景

- Java 21 / Maven 3.9.9 / Spring Boot 3.2.12
- Spring Cloud 2023.0.6 / Spring Cloud Alibaba 2023.0.3.4 / Nacos
- 原生 Spring WebSocket (`TextWebSocketHandler`)，默认握手 `/ws`
- RabbitMQ/Spring AMQP、Inbox/Outbox、Publisher Confirm/Return、Retry/DLQ
- Redis、MyBatis-Plus、Actuator、Micrometer、OpenTelemetry
- JUnit 5、Mockito、AssertJ、Spring Boot Test、Spotless、Docker 分层 Jar

参考项目的 `micro-parent` 版本在 POM 与 README 中不一致，实际版本需通过 effective POM 后再冻结。

## 快速开始

```text
/start
/prd 增加一个需要认证的 WebSocket 消息能力
# 人工补齐 [待确认]，再执行：
/prd-check @docs/prds/<module>.md
/plan @docs/prds/<module>.md
/plan-check @docs/tasks/<tasks>.json
/code @docs/tasks/<tasks>.json
/test workspace/src/main/java/<base-package>/<module>
/review workspace/src/main/java/<base-package>/<module>
/security-gate
/build --profile test
/deploy --env staging
/release v2.0.0
```

目标服务接入后，构建验证以 `./tools/backend.sh validate`、`./tools/backend.sh spotless:check`、`./tools/backend.sh test`、`./tools/backend.sh verify` 为准。当前仓库不创建示例服务，因此不能宣称 Maven 构建已通过。

## 目录

- `.workflow-manifest.yml`：母版领域、workspace 路径、活跃输入和安装策略
- `.claude/`：命令、规则、代理、hooks、工作流拓扑
- `docs/`：PRD、任务、协议索引、测试/安全报告和学习示例
- `tools/`：workspace Maven 包装命令和安全安装脚本
- `templates/`：可选 GitLab/GitHub CI 与部署适配模板
- `workspace/`：后端 Java/Maven 工程唯一容器（母版中只保留 README 和插槽）

详见 [docs/WORKFLOW.md](docs/WORKFLOW.md)、[CLAUDE.md](CLAUDE.md) 和 [.claude/rules/](.claude/rules/)。

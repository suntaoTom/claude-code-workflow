# Java 后端工作流操作手册

> 这套流程面向 Java 后端能力、原生 WebSocket 服务和 RabbitMQ 消息治理。参考项目是技术背景，不是当前仓库工作区。

## 快速开始

母版复制到具体项目后，先把后端工程放入 `workspace/`，填写 `docs/backend-project-profile.yml`，并从仓库根目录启动 Claude Code。母版本身没有 `workspace/pom.xml`，因此不会执行 Maven。

```text
/start
/prd 增加一个需要认证的 WebSocket 消息能力
# 人工补齐 [待确认]，核对上游契约后：
/prd-check @docs/prds/<module>.md
/plan @docs/prds/<module>.md
/plan-check @docs/tasks/tasks-<module>-<date>.json
/code @docs/tasks/tasks-<module>-<date>.json
/test workspace/src/main/java/<base-package>/<module>
/review workspace/src/main/java/<base-package>/<module>
/security-gate --base main
/build --profile test
/deploy --env staging --ci gitlab
/release v2.0.0
```

### 门禁脚本

母版提供确定性检查：

```bash
python3 tools/validate-prd.py docs/prds/<module>.md
python3 tools/validate-tasks.py docs/tasks/<tasks>.json
python3 tools/check-traceability.py
```

脚本负责结构、领域、路径、依赖图和锚点事实；AI 负责业务语义、上游冲突和方案判断。输出 `NOT_APPLICABLE` 代表母版尚未接入业务工程，不代表构建或代码通过。



### 1. `/prd`：需求 → 后端能力需求书

明确调用方、HTTP/WebSocket/RabbitMQ 边界、鉴权、schema、错误码、事务、幂等、超时、重试/DLQ、Redis、SLA、指标、兼容性和配置。未知项写 `[待确认]`，不要猜；上游引用必须有真实路径和锚点。

### 2. `/plan`：需求 → 任务清单

`/prd-check` 通过后，把能力拆为 `contract → schema/config/migration → domain/dao → service → controller/websocket/messaging → unit/integration/contract-test → docker/ci/deploy`。共享 `pom.xml`、application 配置、协议、migration 和 README 串行收口。

### 3. `/code`：任务 → Java

使用 Maven 标准布局、构造器注入、DTO/Form/BO/DO/VO 边界和 JavaDoc 追溯锚点。原生 WebSocket 默认是 `TextWebSocketHandler`，不是 STOMP/SockJS；消息 Payload 不透明转发。RabbitMQ 需要明确 Inbox/Outbox、Confirm/Return、ack、幂等、重试和 DLQ。

### 4. `/test`：规则 → 验证

每条可自动化 `@rules` 一个 JUnit 用例。按需使用 Spring Boot Test、MockMvc、Spring Mock WebSocket、数据库/Redis/RabbitMQ 集成测试和契约测试。真实生产依赖、负载、多节点、灾备和发布切换进入人工 checklist。

### 5. `/review`：质量审查

审查分层、事务、SQL/索引、缓存、WebSocket 生命周期和权限、RabbitMQ 可靠性、配置、日志脱敏、协议兼容、JavaDoc、测试和 Spotless。发现问题走 `/fix`，审查本身不改源码。

### 6. `/security-gate`：变更安全门禁

只扫当前 diff 的 Secret、日志 PII/完整 Payload、反序列化、动态 SQL、SSRF、Actuator、WebSocket Origin/身份、Rabbit/Redis/数据库暴露、镜像和依赖风险。Critical 不为零不得 build。

### 7. `/build`：构建产物

```bash
./tools/backend.sh validate
./tools/backend.sh spotless:check
./tools/backend.sh test
./tools/backend.sh verify
./tools/backend.sh package
```

按需构建分层 Docker 镜像，记录 JAR checksum、commit、镜像 digest、测试报告和 SBOM。

### 8. `/deploy` / `/release`：交付与发布

GitLab CI 与 GitHub Actions 均可保留，但同一环境只能一个入口部署。staging 先部署再查 Actuator health/readiness、关键 API、WebSocket `/ws`、RabbitMQ/Redis/数据库/Nacos；production 必须审批，灰度每阶段停下等待，不自动回滚。发布记录 artifact、镜像、migration、协议兼容和回滚限制。

## Bug 支流

`/bug-check` 先将故障固化为含 traceId/messageId/correlationId/queue/DLQ/事务状态的脱敏报告；`/fix` 先写失败 JUnit/集成测试，再做最小修复。PRD 未定义的行为不是 bug，回到 `/prd`。

## 并发原则

无依赖、不写同一文件、无顺序推理的任务可并行；`pom.xml`、配置、协议、migration、README、任务状态和 CI 入口永远由主 agent 串行收口。

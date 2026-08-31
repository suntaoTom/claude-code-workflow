# Java 后端工作流新人入职指南

> 第一次接触本项目时，按本文从上到下执行。不要一开始阅读整个仓库，也不要在没有 `workspace/pom.xml` 时直接执行 `/code`、`/test` 或 `/build`。

## 1. 先理解项目边界

本仓库是 Java 后端 AI 研发母版，不是具体业务服务源码：

```text
根目录
├── .claude/                    # AI 命令、规则、Agent、Hook 和拓扑
├── CLAUDE.md                  # AI 总规则
├── docs/                      # PRD、任务、测试、安全和协议工作流产物
├── tools/                     # 校验器、Maven 包装器和安装工具
├── templates/                 # 可选 CI/CD 和部署模板
└── workspace/                 # 具体 Java 后端项目唯一容器
```

边界原则：

- 根目录不放业务 Java 源码。
- `workspace/` 放 `pom.xml`、Java 源码、Spring 配置、测试、Docker 和服务自身文件。
- 根 `docs/` 放 AI 研发过程产物；`workspace/docs/`（如有）放具体服务自身文档。
- 不在 `workspace/` 内嵌第二个 `.git`。

## 2. 第一次只读这些文件

按顺序阅读：

1. [README.md](../README.md)：了解母版定位和目录边界。
2. [CLAUDE.md](../CLAUDE.md)：了解 AI 必须遵守的项目规则。
3. [docs/WORKFLOW.md](WORKFLOW.md)：了解日常开发阶段。
4. [docs/backend-project-profile.yml](backend-project-profile.yml)：了解项目适配信息。
5. [workspace/README.md](../workspace/README.md)：了解后端工程插槽。

需要深入某一类任务时再阅读：

- 普通 Java 分层：`coding-style.md`、`tech-stack.md`、`file-docs.md`
- WebSocket/RabbitMQ：`reliability.md`、`security.md`
- 测试：`testing.md`
- 变更和协议来源：`upstream-fidelity.md`

## 3. 从仓库根目录启动 Claude

```bash
cd /path/to/ai-java-backend-workflow
claude
```

必须从包含 `.claude/` 和 `CLAUDE.md` 的根目录启动，不要从 `workspace/` 内部启动。

## 4. 第一个命令永远是 `/start`

```text
/start
```

`/start` 只读扫描：

- `docs/backend-project-profile.yml`
- `workspace/pom.xml`
- `workspace/src/main/java`
- `workspace/src/main/resources`
- `workspace/src/test/java`
- `workspace/src/test/resources`
- `workspace/Dockerfile`
- Java domain task 和 CI/CD 配置

它不会主动编码。扫描结束后，先根据下面的状态分流。

## 5. 判断 workspace 状态

### 状态 A：已经接入 Java 项目

确认存在：

```text
workspace/pom.xml
workspace/src/main/java/
workspace/src/main/resources/
workspace/src/test/java/
```

先填写 [backend-project-profile.yml](backend-project-profile.yml)：

```yaml
project:
  name: "实际服务名"
  root: workspace
  basePackage: "实际 Java 包名"
```

然后运行确定性检查：

```bash
python3 tools/check-traceability.py
./tools/backend.sh validate
```

如果使用 Maven Wrapper，`tools/backend.sh` 会优先使用 `workspace/mvnw`；否则使用系统 Maven。

### 状态 B：母版尚未接入 Java 项目

如果没有 `workspace/pom.xml`，这是正常的母版状态，不是构建失败。

此时不要执行：

```text
/code
/test
/build
/deploy
```

应该先将具体后端工程放入：

```text
workspace/
```

或者用安装脚本初始化目标目录：

```bash
./tools/install-java-backend-workflow.sh /path/to/target-repository --dry-run
./tools/install-java-backend-workflow.sh /path/to/target-repository
```

## 6. 新功能的标准流程

### 第一步：写后端需求书

```text
/prd 增加一个需要认证的 WebSocket Ping/Pong 能力
```

需求中要明确适用内容：

- HTTP、WebSocket、RabbitMQ、定时任务或内部调用
- 鉴权和权限
- 请求/响应或消息 schema
- 错误码、关闭码和异常行为
- messageId、idempotency key、correlationId、traceId
- 事务、数据库、Redis、Inbox/Outbox
- 超时、重试、退避、DLQ
- 性能、SLA、指标和日志脱敏
- 兼容性、迁移和回滚

不确定的内容标为 `[待确认]`，不要猜。

### 第二步：检查 PRD

```bash
python3 tools/validate-prd.py docs/prds/<module>.md
```

通过后再执行：

```text
/prd-check @docs/prds/<module>.md
```

确定性脚本检查结构、domain、占位符、路径和冲突；AI 继续检查上游语义和评审证据。

### 第三步：拆分 Java 任务

```text
/plan @docs/prds/<module>.md
```

任务通常按以下顺序：

```text
contract
  → schema/config/security/migration
  → domain/dao
  → service
  → controller/websocket/messaging
  → unit-test/integration-test/contract-test
  → docker/ci/deploy
```

### 第四步：检查任务

```bash
python3 tools/validate-tasks.py docs/tasks/<tasks>.json
```

通过后：

```text
/plan-check @docs/tasks/<tasks>.json
```

task 必须：

- 顶层包含 `domain: java-backend`
- 使用 `workspace/` 路径
- 有 `prdRef`、`businessRules` 和 `acceptanceCriteria`
- 依赖无环、无悬挂、无前向引用
- 不与其他 task 重复拥有 `pom.xml`、Spring 配置、协议、migration 或 README

### 第五步：实现 Java

```text
/code @docs/tasks/<tasks>.json
```

AI 应该在以下路径生成代码：

```text
workspace/src/main/java/<base-package>/
workspace/src/main/resources/
```

并遵循：

- 构造器注入
- Controller → Service → DAO 单向分层
- DTO/Form/BO/DO/VO 边界
- JavaDoc `@prd/@task/@api/@rules`
- 配置通过 profile/Nacos/Secret 注入
- 不记录 Token、密码、完整 Payload 或 PII

### 第六步：测试

```text
/test workspace/src/main/java/<base-package>/<module>
```

测试放在：

```text
workspace/src/test/java/<base-package>/
```

使用：

- JUnit 5
- Mockito
- AssertJ
- Spring Boot Test
- MockMvc
- Spring Mock WebSocket
- 数据库/Redis/RabbitMQ 集成测试
- API/WebSocket/RabbitMQ 契约测试

测试断言唯一来自 JavaDoc 的 `@rules`。真实生产依赖、多节点、负载和灾备行为进入人工 checklist。

### 第七步：审查和安全门禁

```text
/review workspace/src/main/java/<base-package>/<module>
/security-gate --base main
```

Review 重点：

- 分层和事务
- SQL、索引、N+1
- WebSocket 握手、心跳、关闭和连接限制
- RabbitMQ ack、幂等、重试和 DLQ
- Redis TTL、锁和 Presence
- 日志脱敏
- JavaDoc 和测试追溯

Security Gate 重点：

- Secret 和连接串
- 反序列化
- 动态 SQL
- SSRF
- Actuator 暴露
- RabbitMQ/Redis/数据库管理面
- Docker 和依赖安全

## 7. Maven 构建

```bash
./tools/backend.sh validate
./tools/backend.sh spotless:check
./tools/backend.sh test
./tools/backend.sh verify
./tools/backend.sh package
```

构建产物应记录：

- JAR 路径和 checksum
- commit SHA
- Docker image digest
- 测试报告
- 可选 SBOM

当前母版没有 `workspace/pom.xml` 时，构建命令应明确提示“后端项目尚未接入”，不能伪造成功。

## 8. Bug 修复流程

发现故障时不要直接改源码：

```text
/bug-check <故障描述>
```

真 Bug 报告应包含：

- 服务、版本、profile、环境
- 复现步骤和期望/实际
- traceId/requestId
- messageId/correlationId
- WebSocket 消息或 API
- RabbitMQ exchange/queue/routing key
- Inbox/Outbox/DLQ 状态
- 数据库事务状态
- 脱敏日志和堆栈

确认报告后：

```text
/fix @docs/bug-reports/<report>.md
```

`/fix` 先在 `workspace/src/test/java` 固化失败测试，再修改 `workspace/src/main/java`。

## 9. 部署和发布

部署前先确认：

- profile 已填写
- JAR/镜像来自当前 commit
- CI 主入口已确定
- staging/production 环境已配置
- Actuator health/readiness 可访问
- WebSocket `/ws` smoke test 已定义
- migration 和消息协议可回滚/兼容

```text
/build --profile test
/deploy --env staging --ci gitlab
/release v2.0.0
```

当前部署 adapter 未配置时，`/deploy` 应阻塞，不要把“已触发 CI”写成“已部署”。Production 必须人工审批，失败不自动回滚。

## 10. 新人成长路径

```text
第 1 次：阅读 README、CLAUDE、WORKFLOW
第 2 次：执行 /start，了解 workspace 和 profile
第 3 次：阅读 WebSocket Ping/Pong Golden Path
第 4 次：演练 /prd → /plan → /test
第 5 次：接入真实 Java 项目
第 6 次：完成第一个真实小功能
第 7 次：完成一次 Bug 修复
第 8 次：完成 Review + Security Gate
第 9 次：参与 staging 构建和健康检查
第 10 次：接触生产部署和发布
```

## 11. 新人常见错误

| 错误 | 正确做法 |
|------|----------|
| 从 `workspace/` 启动 Claude | 从仓库根目录启动 |
| 没有 POM 就执行 `/code` | 先接入 Java 项目并填写 profile |
| 直接根据源码猜业务规则 | 从 PRD 和 `@rules` 获取断言 |
| 把完整 Payload 写入日志 | 只记录脱敏元数据 |
| 把 PRD 漏规则当成 Bug | 回到 `/prd` 补充规则 |
| 多个 task 同时修改 POM/配置 | 主 agent 串行收口共享文件 |
| 把部署 placeholder 当成功 | 未配置 adapter 时保持 BLOCKED |
| 复制母版时覆盖已有项目文件 | 先 `--dry-run`，再使用安装脚本 |

## 12. 学习完成标准

新人完成以下事项后，基本掌握这套框架：

- 能解释根目录与 `workspace/` 的边界；
- 能独立填写 `backend-project-profile.yml`；
- 能从 PRD 生成并检查 Java task；
- 能解释 JavaDoc `@rules` 到 JUnit 的追溯链；
- 能区分 WebSocket、RabbitMQ、数据库和缓存测试边界；
- 能识别必须停下来问人的架构决策；
- 能运行 validator 和 `tools/backend.sh`；
- 能看懂 Review、Security Gate、Build 和 Deploy 的结果；
- 不会把未执行、未配置或人工验证事项写成 PASS。

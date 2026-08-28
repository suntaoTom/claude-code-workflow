# .github/ — Java 后端 CI/CD 配置

本目录保留 GitHub Actions 入口，与 GitLab CI 并行支持；同一环境必须只启用一套部署入口。

## 文件清单

| 文件 | 作用 | 状态 |
|------|------|------|
| [workflows/ci-java.yml](workflows/ci-java.yml) | JDK 21 + Maven validate/Spotless/test/verify | ✅ |
| [workflows/deploy-java.yml](workflows/deploy-java.yml) | JAR/Docker 构建、环境审批和健康检查契约 | 🟡 需配置目标平台 |
| [workflows/claude-fix.yml](workflows/claude-fix.yml) | Issue 触发 `/fix --headless` | 🟡 需配置 Anthropic secret |
| [pull_request_template.md](pull_request_template.md) | Java 后端 PR/MR 追溯与验证清单 | ✅ |

迁移前的 web/iOS/Android/Harmony workflow 已移出活跃入口；当前仓库不创建 Java 示例服务，CI 在不存在 `workspace/pom.xml` 时不宣称构建通过。

## GitHub 配置

- `ANTHROPIC_API_KEY` 只放 repository/environment secret，不写 workflow、prompt 或日志。
- production 使用 Environment Required reviewers。
- 镜像仓库、部署平台、staging/prod URL、Nacos/RabbitMQ/Redis/MariaDB 凭据使用 environment variables/secrets。
- GitHub 与 GitLab 不得对同一 environment 同时自动部署；选择一个为发布源。

## 验证标准

Java 工程接入后至少通过 `mvn validate`、`mvn spotless:check`、`mvn test`、`mvn verify`；部署后验证 `/actuator/health`、readiness、关键 API、WebSocket `/ws`，并记录 commit、JAR checksum 和镜像 digest。

## Claude Fix 安全边界

触发者白名单、draft PR、最小工具权限和禁止 force push/main reset 规则保持；`/fix` 只接收脱敏故障报告，默认不触碰 CI/Secret/部署配置。详见 `.claude/commands/fix.md`。

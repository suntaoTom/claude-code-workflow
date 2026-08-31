---
name: ext-changelog
description: 生成 Java 后端变更影响报告，按 Maven 包/模块聚合 commit，识别 API、消息、数据库、配置和部署风险；用户明确要求变更报告/周报/交接时触发。
---

# ext-changelog — Java 后端变更影响报告

面向理解、周报、交接和复盘；与 `/release` 的版本发布 changelog 分开。git 数据由脚本获取，AI 负责按后端模块解释。

## 执行

```bash
bash .claude/skills/ext-changelog/scripts/range-commits.sh [since] [scope] [author]
bash .claude/skills/ext-changelog/scripts/changed-files.sh [since] [scope]
```

默认 scope 为 `.`；后端模块 scope 示例为 `workspace/src/main/java/<base-package>/<module>/`。

## 聚合规则

按以下路径分类：

- `workspace/src/main/java/**/controller/` → controller
- `workspace/src/main/java/**/service/` → service
- `workspace/src/main/java/**/dao/` 或 `repository/` → persistence
- `workspace/src/main/java/**/domain/` → domain
- `workspace/src/main/java/**/infra/` 或 `config/` → infrastructure
- `workspace/src/main/resources/` → configuration
- `workspace/src/test/` → tests
- `docs/contracts/` → contracts
- `workspace/` 其他文件 → backend-project
- `.claude/`、根 `docs/`、tools → workflow

解析 `type(scope): description`，关联 PRD、task、Bug、API/WebSocket/RabbitMQ contract、migration、测试报告和发布证据。重点识别：跨层修改、未关联需求、配置/协议/数据库兼容影响、WIP/TODO/FIXME、未验证集成环境和潜在部署风险。

## 输出

报告包含范围、按 Java 模块的变更故事、Bug、协议/数据库/配置影响、测试和安全证据、未验证项、回滚风险及统计。只读 git，不改代码。

## 示例

```text
/ext-changelog
/ext-changelog --since 2026-08-01
/ext-changelog workspace/src/main/java/io/github/microboot/websocket/
/ext-changelog --author alice --since 2026-08-14
```

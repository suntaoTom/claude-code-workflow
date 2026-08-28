# .claude/ — Java 后端自动化配置

> Claude Code 工作流配置中心。目录职责保持通用，内容以 Java 后端为领域基线。

## 目录清单

| 目录/文件 | 职责 | 触发方式 |
|----------|------|---------|
| [commands/](commands/) | PRD、计划、编码、测试、审查、构建和交付命令 | 用户显式输入 `/<name>` |
| [skills/](skills/) | 需要脚本/外部数据的扩展能力 | 显式或按 description 自动调用 |
| [agents/](agents/) | 测试、审查、修复、元审计子代理 | 主命令 `Agent` spawn |
| [hooks/](hooks/) | Java/配置/任务状态快速检查 | `settings.json` 事件触发 |
| [rules/](rules/) | Java、可靠性、安全、测试与文件说明规范 | `CLAUDE.md` 按需引用 |
| [workflow.json](workflow.json) | 主线、Bug 支流和独立工具拓扑 | 人工维护 |
| [settings.json](settings.json) | 团队共享 hooks 配置 | Claude Code 启动时加载 |

## 主线

`prd → prd-check → plan → plan-check → code → test → review → security-gate → build → deploy → release`

## 当前领域基线

Java 21 / Maven 3.9.9 / Spring Boot 3.2.12 / Spring Cloud Alibaba + Nacos / 原生 Spring WebSocket / RabbitMQ / Redis / MyBatis-Plus / Actuator / Micrometer / OpenTelemetry / JUnit 5 / Spotless / Docker。参考项目仅作背景，不作为本仓库依赖。

## 共享文件规则

README、workflow 拓扑、规则索引、任务状态、Maven 配置、Spring 配置、消息协议和 CI 入口由主 agent 串行收口；独立模块的 Java 源码、测试和报告在不共享文件时可并行。

## 当前项目状态

- **命令**：`prd`、`prd-check`、`plan`、`plan-check`、`code`、`test`、`review`、`security-gate`、`bug-check`、`fix`、`build`、`deploy`、`release`、`start`、`meta-audit`
- **代理**：`test-writer`、`code-reviewer`、`bug-fixer`、`meta-auditor`
- **钩子**：`check-hardcode`、`check-tasks-status`、`pre-commit-check`、`format`
- **规则**：`coding-style`、`file-docs`、`no-hardcode`、`tech-stack`、`testing`、`reliability`、`security`

前端视觉/a11y 资产若作为历史保留，必须在对应 README 标明“迁移前历史”，不能作为当前后端流程入口。

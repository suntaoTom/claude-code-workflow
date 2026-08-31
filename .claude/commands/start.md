---
description: Java 后端项目入职向导 — 扫描 Maven、模块、配置、依赖和任务状态
allowed-tools: Read, Bash, Glob, Grep
helper: true
---

你刚加入 Java 后端项目，请只读完成入职扫描，不主动编码。

## 扫描范围

1. `workspace/pom.xml`：Java/Maven/Spring/Starter/插件/私有仓库和 profile。
2. `workspace/src/main/java`：包结构、Controller/Service/DAO/Domain/Infra/Config、入口和依赖方向。
3. `workspace/src/main/resources`：application/profile/Nacos、WebSocket、RabbitMQ、Redis、Actuator；只报告配置键，不输出 Secret 值。
4. `workspace/src/test/java` 与 `workspace/src/test/resources`：JUnit、Spring Boot、数据库/Redis/RabbitMQ/WebSocket/契约/集成测试。
5. Docker、GitLab/GitHub CI、部署/运行文档；确认构建、健康检查、`/ws` smoke test 和外部依赖。
6. `docs/tasks/*.json`：只扫描顶层 `domain: java-backend` 的任务文件；没有该字段的旧前端任务视为迁移历史，不参与当前状态汇总。按模块汇总 pending/in-progress/done/blocked，检查依赖和最近状态。

## 输出

报告技术栈、模块边界、配置入口、运行命令、测试命令、外部依赖、风险（包括单实例/粘性路由和版本冲突）以及任务统计。优先读取 `docs/backend-project-profile.yml`，再按 profile 中的路径扫描。当前仓库未初始化 workspace Java 服务时，明确说明这一点并等待后续指令。

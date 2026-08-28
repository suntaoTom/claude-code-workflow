# 文件与模块说明规范（Java 后端）

每次创建或修改 Java、配置、迁移、测试或脚本文件时，必须同步维护所在目录 `README.md` 的文件清单；共享 README 由主 agent 串行收口。

## Java 文件头 JavaDoc

```java
/**
 * @description 处理 WebSocket 入站消息并提交业务服务。
 * @module infra.websocket
 * @dependencies WebsocketSessionManager, MessageService
 * @prd docs/prds/realtime-message.md#入站消息处理
 * @task docs/tasks/tasks-realtime-message-YYYY-MM-DD.json#T005
 * @api docs/apis/websocket.md#inbound-message
 * @rules
 *   - 未通过身份校验的连接不得进入业务消息处理。
 *   - 重复 messageId 不得重复产生业务副作用。
 */
```

要求：

- `@prd` 指向真实 PRD 二级标题；`@task` 指向真实 task ID；`@api` 指向真实 OpenAPI、WebSocket schema 或消息契约锚点。
- `@rules` 只写业务规则，尽量照抄 PRD 原文；不写“使用某个类/注解”等实现细节。
- 配置类、消息处理器、DAO、数据库迁移和集成测试也要挂载适用锚点。
- 纯工具可省略业务锚点，但必须说明参数、返回值和边界。
- 公共包添加 `package-info.java`，说明职责和允许的依赖方向。

## 目录 README

每个功能目录至少维护：

```markdown
# 目录名称

> 一句话描述职责

## 文件清单

| 文件名 | 说明 | 依赖 | 最后更新 |
|--------|------|------|----------|
| MessageHandler.java | WebSocket 消息入口 | Service | YYYY-MM-DD |

## 模块关系

> 本目录与其他层的依赖方向和事务/消息边界。
```

## 模块 README

`workspace/src/main/java/<base-package>/` 及 `controller/`、`service/`、`dao/`、`domain/`、`infra/`、`config/` 等目录需要说明职责、核心流程、对外暴露和依赖方向。测试目录 README 说明测试分层、外部依赖和启动方式。

## 追溯要求

链路必须保持：`PRD 锚点 → taskId → JavaDoc @prd/@task/@api/@rules → JUnit 测试方法 → 测试报告矩阵`。引用不存在的文件、章节、operationId 或消息类型视为阻塞问题；遇到上游冲突必须停止并进入 `## 冲突待决`，不能自行改写。

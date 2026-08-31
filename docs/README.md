# docs/ — Java 后端工作流产物

## 目录结构

```text
docs/
├── WORKFLOW.md
├── ADAPTING.md
├── DECISIONS.md
├── backend-project-profile.yml # workspace/Maven 项目适配配置
├── contracts/            # OpenAPI/WebSocket/RabbitMQ 协议源
├── examples/             # 文档级 Golden Path，不参与业务构建
├── prds/                 # 后端能力/API/消息需求书
├── tasks/             # /plan 生成的 Java 后端任务清单（详见 tasks/README.md）
├── bug-reports/       # /bug-check 规范化故障报告
├── test-reports/      # JUnit/集成结果和人工 checklist
├── reports/security/  # /security-gate 安全门禁报告
└── retrospectives/    # /meta-audit 不可变审计快照
```

## 追溯链

```text
上游产品/协议/架构 → PRD 锚点 → taskId → JavaDoc @prd/@task/@api/@rules → JUnit @Test → 测试报告
```

根 `docs/` 记录 AI 研发过程；`workspace/docs/`（如存在）只记录具体 Java 服务自身的运行/架构文档。`workspace/` 是后端工程唯一容器，详见 [workspace/README.md](../workspace/README.md)。


## 任务清单

任务文件 `tasks-<module>-<YYYY-MM-DD>.json` 使用 `contract/schema/config/migration/domain/dao/service/controller/websocket/messaging/cache/test/ci/deploy` 等后端类型，状态为 `pending/in-progress/done/blocked`。共享 `pom.xml`、Spring 配置、协议、migration 和 README 由主 agent 收口。

## 测试与故障

`/test` 报告 JUnit、Spring、数据库、Redis、RabbitMQ、WebSocket 和契约测试；真实生产、负载、多节点和发布验证进入人工 checklist。`/bug-check` 报告只能包含脱敏证据，`/fix` 先固化失败测试再改源码。

## 历史

迁移前的前端 PRD、任务清单、测试报告和元审计报告作为不可变历史保留，不代表当前 Java 后端规范。没有 `domain: java-backend` 的旧任务不参与当前状态扫描；新增内容不得继续引用其页面、Umi、React 或移动平台流程。

# docs/ — Java 后端工作流产物

## 目录结构

```text
docs/
├── WORKFLOW.md
├── ADAPTING.md
├── DECISIONS.md
├── prds/              # 后端能力/API/消息需求书
├── tasks/             # /plan 生成的任务清单
├── bug-reports/       # /bug-check 规范化故障报告
├── test-reports/      # JUnit/集成结果和人工 checklist
└── retrospectives/    # /meta-audit 不可变审计快照
```

## 追溯链

```text
上游产品/协议/架构 → PRD 锚点 → taskId → JavaDoc @prd/@task/@api/@rules → JUnit @Test → 测试报告
```

所有引用必须指向真实文件、行号或锚点。上游冲突必须进入 `## 冲突待决`，不能自行改写。

## 任务清单

任务文件 `tasks-<module>-<YYYY-MM-DD>.json` 使用 `contract/schema/config/migration/domain/dao/service/controller/websocket/messaging/cache/test/ci/deploy` 等后端类型，状态为 `pending/in-progress/done/blocked`。共享 `pom.xml`、Spring 配置、协议、migration 和 README 由主 agent 收口。

## 测试与故障

`/test` 报告 JUnit、Spring、数据库、Redis、RabbitMQ、WebSocket 和契约测试；真实生产、负载、多节点和发布验证进入人工 checklist。`/bug-check` 报告只能包含脱敏证据，`/fix` 先固化失败测试再改源码。

## 历史

迁移前的前端 PRD、测试报告和元审计报告作为不可变历史保留，不代表当前 Java 后端规范。新增内容不得继续引用其页面、Umi、React 或移动平台流程。

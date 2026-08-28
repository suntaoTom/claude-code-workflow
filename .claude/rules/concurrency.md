# 并发执行策略：串行 vs 并行（通用规则）

适用于 `/code`、`/test`、`/review`、`/fix` 及本仓库的多个独立任务。默认追求并行，但依赖、共享文件或顺序推理任一成立就串行。

## 三个必要条件

两个工作单元只有同时满足以下条件才能并行：

1. DAG 中无直接/传递依赖；
2. 不写同一文件，也不写同一共享资源；
3. 不需要先看另一个结果再决定本任务方案。

## Java 后端拓扑

常见功能链：

```text
contract → schema/config/migration → domain/dao → service
→ controller/websocket/messaging → unit/integration/contract-test
→ docker/ci/deploy
```

链内串行；不同模块在依赖已完成且文件不重叠时并行。

## 必须主 agent 串行收口

- `pom.xml`、Maven parent/BOM、依赖锁定和 CI 总入口
- `application*.yml`、Nacos/profile、Secret 引用和部署配置
- 公共 DTO/VO、错误码、WebSocket/RabbitMQ 契约、exchange/queue/topology
- 数据库 migration 顺序、公共 schema、Outbox/Inbox 状态定义
- 目录 README、package-info、任务 JSON 的 status、全局索引和汇总报告

并行 agent 只写自己被分配的 Java/测试文件，并回报需收口的 README/协议/配置行。

## 何时不并行

任务少于 3 个、文件高度重叠、线性依赖链、需要探索式顺序推理或成本敏感时直接串行。多个 bug 共享配置/协议/migration 时也串行。

## 失败隔离

一个 agent 失败不影响同批其他任务；主 agent 收集结果，必要时单独重试或标记 blocked。每批结束统一校验 `mvn validate`/Spotless/相关测试，未接入 workspace 时明确跳过，不虚报。

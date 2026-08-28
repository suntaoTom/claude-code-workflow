# Java 后端编码规范

## 命名与结构

- 类、接口、枚举 UpperCamelCase；方法、参数、局部变量 lowerCamelCase；常量 UPPER_SNAKE_CASE。
- 包按职责组织：`controller`、`service`、`dao`、`domain`、`infra`、`config`。
- Controller/Handler 负责入口协议适配，Service 负责业务编排，DAO 负责持久化，Infra 负责外部系统适配。
- DTO、Form、BO、DO、VO 各自表达边界，不为省转换而暴露内部对象或敏感字段。
- 构造器注入优先，依赖字段尽量 `final`；禁止无理由字段注入。

## Java 与 Spring

- 遵循 Alibaba Java Coding Guidelines 和现有项目约定；不要为尚未发生的需求预留复杂抽象。
- 配置类使用 Spring 配置绑定和 profile；业务代码不读取环境变量并散落转换逻辑。
- 事务边界落在 Service，读写一致性、消息发布与 Outbox 关系必须在任务和 JavaDoc 中说明。
- Bean 生命周期、线程池、定时任务、WebSocket Session 和 Redis 资源必须有明确释放/停止策略。
- 异步流程区分业务异常、参数异常和基础设施异常；不得用空 catch 或宽泛 catch 隐藏失败。

## 异常与日志

- 异常保留原始 cause；向外映射时不得泄露内部堆栈、凭据或连接细节。
- 使用 SLF4J 参数占位符，不拼接敏感数据；不使用 `System.out` 或 `printStackTrace`。
- 日志默认只记录可追踪元数据（traceId、messageId、类型、状态、耗时）；Token、密码、完整消息 Payload、手机号/身份证等 PII 必须脱敏或不记录。
- RabbitMQ 消费失败不能静默吞掉；ack、重试、DLQ 结果必须可观察。

## WebSocket 与消息

- 握手身份、用户类型、Origin、连接数、消息大小、频率、心跳和关闭原因必须配置化。
- 不把业务 Payload 的解释混入传输层；仅按显式协议和注册路由转发。
- messageId、idempotency key、correlationId、traceId 语义不可混淆。
- RabbitMQ 生产/消费必须说明 Confirm/Return、Inbox/Outbox、幂等、重试上限和 DLQ 终态。
- 多实例场景不得假设 JVM 本地 Map 可共享；临时回复路由必须有单实例/粘性路由前提或外部化方案。

## 注释与质量

- 注释解释“为什么”，不复述代码；复杂并发、兼容、绕过和协议约束必须说明原因。
- 公共类、入口组件、配置类、消息处理器、DAO 和迁移脚本使用 JavaDoc 维护 `@prd/@task/@api/@rules`。
- Spotless 是格式基线；不要提交无关格式化、构建产物、日志或本地配置。

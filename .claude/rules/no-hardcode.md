# P0：禁止硬编码（Java 后端）

所有会随环境、租户、部署、协议版本或运营策略变化的值，都必须通过 Spring 配置、profile、Nacos、Secret、集中常量或协议契约提供；配置本身也要 DRY，不能多处复制。

## 禁止硬编码

### 凭据与连接

- 数据库、Redis、RabbitMQ、Nacos 的 URL、用户名、密码、vhost、namespace。
- JWT secret、签名密钥、私钥、AccessKey、Webhook token。
- 生产环境域名、内部地址和云资源 ID。

### 可靠性与安全策略

- WebSocket 握手路径、Origin 白名单、单用户/单 IP 连接上限。
- 心跳间隔、超时、消息字节上限、限流窗口和阈值。
- RabbitMQ exchange、queue、routing key、TTL、重试次数、退避档位、DLQ。
- 缓存 TTL、锁超时、批量大小、并发度、熔断和限流阈值。
- 错误码、协议版本、业务状态、租户和环境值。

### 日志与测试

- 禁止在日志、异常消息、测试 fixture、示例配置和 PRD 中写 Token、密码、私钥、完整连接串、完整业务 Payload 或 PII。
- 禁止用真实生产凭据让测试“跑通”；使用隔离环境和安全注入。

## 推荐分层

```text
application.yml / profile → 环境变量或 Secret → @ConfigurationProperties → 业务组件
协议固定值 → 版本化契约或集中常量 → 适配器/处理器
```

同一配置只定义一次；模块通过配置绑定或公共常量引用。配置键应在 `application-<profile>.yml` 或远程配置中按环境覆盖，不能复制到 Java 类的魔法数字里。

## 可接受的固定值

只有以下值可保留为集中常量：Java 语言/标准库常量、已发布协议明确不可变的标识、且其来源能在 `@api`、PRD 或 ADR 中追溯。队列名、错误码、超时等仍应集中管理并附来源。

## 检查线索

```bash
grep -RInE '(password|secret|token|private.?key|access.?key|jdbc:|amqp:|redis://|nacos)' src . --exclude-dir=target
grep -RInE '(System\.out|printStackTrace|log\.(info|warn|error).*payload)' src --exclude-dir=target
```

命中只是定位线索，最终须阅读上下文；测试占位符和配置键名不能简单视为泄密。

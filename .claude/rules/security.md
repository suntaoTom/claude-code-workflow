# Java 后端安全规范

## 入口与身份

- HTTP/WebSocket 握手必须校验身份、用户类型、权限和有效期；未授权连接不得进入业务消息处理。
- Origin、连接数、消息大小、频率、超时和可用协议版本必须配置化；生产不得无条件允许任意 Origin，除非网关有可验证的白名单防护。
- 入站消息按显式 schema 和路由处理；拒绝不可信类型、多态反序列化和未知路由猜测。

## 数据与日志

- Token、密码、密钥、Cookie、连接串和 PII 不得进入源码、配置仓库、日志、异常消息、测试 fixture 或 prompt。
- 日志只记录脱敏元数据；禁止打印完整业务 Payload、认证头和敏感请求体。
- Controller/消息入口做输入校验；动态 SQL 使用参数绑定，禁止字符串拼接。

## 运行与供应链

- Actuator 只暴露必要 endpoint；管理端口、RabbitMQ、Redis、MariaDB 不得无意对公网开放。
- 生产 Secret 通过 CI variables、Secret 管理或外部配置注入，不能写进 `application-prod.yml`。
- CI 执行依赖/镜像漏洞扫描；构建产物需记录 commit、checksum、镜像 digest 和依赖来源。
- Docker 运行时使用非 root 用户（若基础镜像支持），不把本地配置和 `target` 无关文件打入镜像。
- WebSocket/RabbitMQ/数据库的授权失败、反序列化失败和 DLQ 事件必须可告警。

## 审查边界

静态扫描命中只是线索，必须阅读上下文；安全风险不得因测试 mock 或“由网关保证”而默默忽略，需在配置/部署/ADR 中有可验证依据。

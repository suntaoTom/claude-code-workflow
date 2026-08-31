# WebSocket Ping/Pong Golden Path（文档示例）

> 仅用于学习母版流程，不创建业务 Java 源码，不参与当前任务扫描，也不代表当前母版已具备可运行服务。

## 示例目标

实现一个经过身份认证的原生 Spring WebSocket 能力：

- 握手路径：`/ws`
- 合法身份可建立连接
- 未认证或用户类型未知的握手被拒绝
- 客户端发送协议 `ping` 后返回 `pong`
- 心跳、消息限制、超时和关闭原因均配置化

## 需求到任务

```text
需求说明
  → /prd
  → /prd-check
  → /plan
  → /plan-check
  → /code
  → /test
  → /review
  → /security-gate
  → /build
```

建议任务链：

```text
contract
  → config/security
  → handshake
  → message-handler
  → heartbeat
  → websocket-integration-test
```

每个 task 顶层必须有：

```json
{
  "domain": "java-backend",
  "filePath": "workspace/src/main/java/<base-package>/...",
  "prdRef": "docs/prds/websocket-ping.md#连接与身份",
  "businessRules": [],
  "acceptanceCriteria": [],
  "dependencies": [],
  "status": "pending"
}
```

## 预期文件位置

```text
workspace/src/main/java/<base-package>/config/WebSocketConfig.java
workspace/src/main/java/<base-package>/ws/HandshakeInterceptor.java
workspace/src/main/java/<base-package>/ws/PingPongHandler.java
workspace/src/test/java/<base-package>/ws/PingPongHandlerTest.java
workspace/src/test/java/<base-package>/ws/WebSocketIntegrationTest.java
```

生产 JavaDoc 应包含 `@prd`、`@task`、`@api`（协议存在时）和 `@rules`；JUnit 测试以 `@rules` 为唯一业务断言来源。

## 验证命令

在真实后端项目接入 `workspace/pom.xml` 后：

```bash
./tools/backend.sh validate
./tools/backend.sh spotless:check
./tools/backend.sh test
./tools/backend.sh verify
./tools/backend.sh run --profile dev
```

运行后人工或 smoke test 验证：

```text
GET /actuator/health
合法身份握手 /ws
未认证握手拒绝
ping → pong
连接超时和关闭资源释放
```

## 当前边界

母版当前没有 `workspace/pom.xml`、Java 源码或测试，因此上述命令在母版中应报告未接入，而不是伪造通过。真实生产认证、跨节点连接、多实例路由、负载、网络故障和发布回滚属于人工/专项验证。

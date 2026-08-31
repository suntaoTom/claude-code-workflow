# 预期 Java 工程布局

Golden Path 只定义目标，不创建业务源码。接入具体服务后，任务应生成：

```text
workspace/src/main/java/<base-package>/config/WebSocketSecurityConfig.java
workspace/src/main/java/<base-package>/ws/PingPongHandler.java
workspace/src/test/java/<base-package>/ws/PingPongHandlerTest.java
```

## JavaDoc 追溯

生产类至少包含：

```java
/**
 * @description 处理原生 WebSocket Ping/Pong。
 * @module websocket
 * @prd docs/examples/websocket-ping/prd.md#能力点-1-认证-websocket-ping-pong
 * @task docs/examples/websocket-ping/tasks.json#T003
 * @api docs/contracts/websocket/ping-pong.json
 * @rules
 *   - 当已建立连接收到协议 ping 时，应返回协议 pong，且不进入业务消息路由。
 */
```

真实项目的 `@prd`、`@task` 和 `@api` 必须指向项目根目录的活跃文件；Golden Path 中的路径只是学习示例。

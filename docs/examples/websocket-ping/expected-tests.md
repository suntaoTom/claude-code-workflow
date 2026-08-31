# 预期测试布局

测试使用 JUnit 5、Mockito、AssertJ 和 Spring Boot Test；测试代码位于：

```text
workspace/src/test/java/<base-package>/ws/PingPongHandlerTest.java
```

## 规则映射

| 规则 | 测试方法示例 | 层级 |
|------|--------------|------|
| 合法连接收到 ping 返回 pong，且不进入业务路由 | `validPingReturnsPongWithoutBusinessDispatch` | 单元/协议 |
| 超过消息大小或频率限制时以策略违规关闭 | `oversizedMessageClosesWithPolicyViolation` | 单元/协议 |
| 缺少身份或用户类型时握手被拒绝 | `handshakeWithoutIdentityIsRejected` | Spring WebSocket 集成 |

每条可自动化 `@rules` 必须有独立 JUnit `@Test`；真实多节点、负载、网络故障和生产 Broker 行为放入人工/专项 checklist，不用 mock 伪装成已验证。

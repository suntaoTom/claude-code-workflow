# WebSocket Ping/Pong Golden Path PRD

## 元信息

| 项 | 值 |
|----|----|
| domain | java-backend |
| 模块代号 | websocket-ping |
| 负责人 | 学习者 |
| 创建日期 | 2026-08-31 |
| 状态 | approved |
| 需求来源 | 教学示例 |

## 背景与目标

为后端研发新人提供一个最小但完整的原生 Spring WebSocket 需求示例，演练认证、协议、连接生命周期、测试和安全门禁。

## 能力点 1：认证 WebSocket Ping/Pong

### 调用与边界

- 调用方：已登录的 WebSocket 客户端。
- 入口：原生 Spring WebSocket，握手路径 `/ws`。
- 鉴权：握手阶段校验用户身份和用户类型；本示例不规定具体 Token 载体。
- 传输层只处理连接和协议消息，不解释业务 Payload。

### 数据与协议

协议源：`docs/contracts/websocket/ping-pong.json`。

| 消息 | 字段 | 类型 | 必填 | 语义 |
|------|------|------|------|------|
| ping | `type` | string | 是 | 固定为 `ping` |
| pong | `type` | string | 是 | 服务端响应，固定为 `pong` |

### 业务规则

1. 当握手身份有效且用户类型受支持时，应允许建立 WebSocket 连接。
2. 当握手缺少身份或用户类型不受支持时，应拒绝建立连接。
3. 当已建立连接收到协议 `ping` 时，应返回协议 `pong`，且不进入业务消息路由。
4. 当连接超过配置的消息大小或频率限制时，应以策略违规关闭连接。

### 可靠性与异常

- 连接注册和关闭必须幂等，重复关闭不能重复释放同一 Session。
- 心跳间隔、超时、消息大小和频率限制必须来自 profile/Spring 配置。
- 非法 JSON 或未知消息类型不得静默进入业务处理；关闭原因或错误必须可追踪。
- 多实例是否共享 Session 路由属于本示例范围外，接入真实项目时必须单独确认。

### 性能与可观测性

- 记录连接建立、关闭、拒绝和消息处理的 traceId、用户类型和耗时，不记录 Token 或完整 Payload。
- 连接数、拒绝数、超时数和协议错误数应可通过指标观察。

## 配置项

| 配置键 | 默认/环境 | Secret? | 来源 |
|--------|-----------|---------|------|
| `websocket.security.handshake-path` | `/ws` | 否 | 本 PRD |
| `websocket.security.max-message-bytes` | `[默认假设]` | 否 | 待项目确认 |
| `websocket.security.max-messages-per-minute` | `[默认假设]` | 否 | 待项目确认 |

## 范围外

- 不实现具体业务消息。
- 不规定 JWT、Cookie 或网关认证的具体实现。
- 不验证真实生产负载、多节点会话迁移、网络故障和生产部署。

## 验收清单

- [ ] 合法身份握手成功。
- [ ] 缺少身份或用户类型时握手被拒绝。
- [ ] ping 返回 pong，且不进入业务路由。
- [ ] 消息大小/频率限制和关闭行为有测试。
- [ ] JavaDoc 追溯到本 PRD 和 task。
- [ ] 真实多节点、负载和部署验证已列入人工 checklist。

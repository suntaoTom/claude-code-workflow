# contracts/ — 后端协议契约

> 这里保存 AI 工作流消费的版本化协议源；不保存 Secret，不放业务 Java 代码。

## 目录

| 目录 | 内容 |
|------|------|
| `openapi/` | HTTP/OpenAPI JSON 主源 |
| `websocket/` | 原生 WebSocket 消息 schema |
| `rabbitmq/` | Exchange、Queue、Routing Key 和消息契约 |

OpenAPI JSON 通过 `python3 tools/gen_api_md.py` 生成 `docs/apis/` 的人类可读索引；生成文件不要手改。真实项目运行文档和业务代码仍放 `workspace/`。

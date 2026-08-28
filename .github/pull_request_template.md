<!--
  Java 后端 PR/MR 模板。字段不适用时写 "-"，不要留空。
-->

## 变更类型

- [ ] feat（新能力）
- [ ] fix（Bug 修复）
- [ ] refactor（不改变外部行为）
- [ ] docs / test / chore

## 追溯

- PRD：`docs/prds/<module>.md#<anchor>`
- 任务：`docs/tasks/<tasks>.json#T00X`
- Bug/Issue：`#xxx` 或 `-`
- API/WebSocket/RabbitMQ 契约：路径、版本、锚点或 `-`

## 变更与影响

- 变更摘要：
- 影响模块/包：`workspace/src/main/java/<base-package>/...`
- 配置/profile 变更：无 / 有（只写配置键，不写 Secret）
- 数据库 migration：无 / 有（版本与兼容策略）
- 消息兼容性：无 / 有（message type、版本、旧消费者行为）
- WebSocket 兼容性：无 / 有（握手、消息、关闭和多实例影响）

## 验证清单

- [ ] `mvn -B -ntp validate`
- [ ] `mvn -B -ntp spotless:check`
- [ ] `mvn -B -ntp test`
- [ ] `mvn -B -ntp verify`（如适用）
- [ ] 规则对应的 JUnit/集成/契约测试已补齐
- [ ] 测试报告和人工 checklist 已更新
- [ ] JavaDoc `@prd/@task/@api/@rules` 与目录 README 已同步
- [ ] 无密钥、Token、连接串、完整 Payload 或 PII 进入代码/日志/提交
- [ ] `/security-gate` 通过（如涉及后端代码/配置）

## 未解决问题与回滚

- 未验证事项：
- 生产/集成环境限制：
- 回滚版本与数据库/消息兼容限制：

<!-- 🤖 Generated with Claude Code (/fix | /code) -->

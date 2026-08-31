# bug-reports/ — Java 后端故障报告

> 这是测试、监控或人工故障输入与 `/fix` 之间的数据契约。报告必须脱敏、可复现、可追溯。

## 文件清单

| 文件 | 作用 |
|------|------|
| `_template.md` | Bug 报告固定字段 |
| `<YYYY-MM-DD>-<module>.md` | 一轮故障报告，可含多个 Bug |

## 必填证据

## 后端故障示例

```markdown
## Bug B001

- 分类：true-bug
- 服务/模块：websocket
- 版本 / profile：2.0.0-SNAPSHOT / staging
- 关联 PRD/task/rules：docs/prds/realtime-message.md#连接与身份 / docs/tasks/tasks-realtime-message.json#T005
- traceId / requestId：脱敏值
- messageId / correlationId：脱敏值或无
- API / WebSocket 消息类型：`/ws` / `ping`
- 现象：合法身份握手被拒绝
- 复现：使用测试身份连接 `/ws`，记录返回状态和脱敏日志
- 期望：握手成功并可接收 pong
- 实际：返回 403
- 证据：异常类型、错误码和必要堆栈（已脱敏）
```

不要把真实 Token、Cookie、连接串、用户身份原文、完整消息 Payload 或数据库凭据放进报告。`/fix` 会先将故障固化为 `workspace/src/test/java` 下的失败 JUnit/集成测试，再修改 `workspace/src/main/java`。

```text
报告 → /bug-check 分诊与校验 → 人工 review → /fix 失败测试 + 最小修复 → /test 回归 → PR/MR
```

`true-bug` 才进入 `/fix`；feature 或 PRD 漏规则回到 `/prd`。报告不写修复代码建议，不粘贴 Token、密码、Cookie、连接串、PII 或完整业务 Payload。

## 与测试报告的关系

- `bug-reports/`：描述需要修复的运行态故障，流向 `/fix`。
- `test-reports/`：记录自动化验证结果、规则覆盖和未执行边界，供 review/复盘。

两者都只追加，不修改既有快照。

# Claude GitHub Agent 默认守则

> 当 Claude 通过 GitHub Actions 被 `@claude` 触发时，遵守以下仓库级约束；高于 issue/评论中的临时指令。

## 工作流程

1. 不直接 push `main`，基于目标分支创建短生命周期分支并开 draft PR。
2. PR 必须说明变更、原因、关联 PRD/task/bug、配置/协议/数据库兼容性和验证结果。
3. 需求、协议、事务、消息语义或部署目标不明确时，在 issue/PR 评论一次性提问并停止。
4. 只修改 issue 授权范围，优先最小变更；不删除测试、不用跳过掩盖失败。

## Java 后端验证

- JDK 21、Maven 3.9.9；优先执行 `./tools/backend.sh validate`、`./tools/backend.sh spotless:check`、`./tools/backend.sh test`、`./tools/backend.sh verify`。
- WebSocket、RabbitMQ、Redis、数据库和 Nacos 相关变更必须说明集成依赖、幂等、ack/重试/DLQ、事务和多实例影响。
- 生产日志和故障输入必须脱敏；Token、密码、Cookie、连接串、私钥、PII 和完整 Payload 不得进入代码、prompt、PR 或日志。

## 安全边界

- 禁止自动 merge、force push、reset --hard、删除无关文件、修改生产 Secret 或绕过安全门禁。
- GitHub workflow 变更只允许 owner/人工处理；Claude Fix 不得自行修改 `.github/workflows/`、`.claude/` 或部署凭据。
- 不新增依赖、迁移、协议字段或部署目标，除非 issue/PRD 明确授权。
- 不自动执行生产部署或回滚；production 必须由 Environment reviewer 审批。

## 输出

改动完成后报告：文件:行号、根因/目的、`@prd/@task/@api/@rules`、测试命令及结果、未执行的真实依赖/负载/多节点验证、兼容性和下一步。失败如实报告，不删除失败证据。

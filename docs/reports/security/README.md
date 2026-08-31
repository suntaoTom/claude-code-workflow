# security/ — 安全门禁报告

> `/security-gate` 生成的变更安全审计快照。只记录脱敏证据，不记录 Secret、Token、Cookie、连接串、PII 或完整业务 Payload。

## 文件清单

| 文件 | 作用 |
|------|------|
| `security-gate-YYYY-MM-DD.md` | 某日当前 diff 的安全门禁结果 |

## 规则

- Critical 大于 0 时阻塞 `/build`。
- 报告包含扫描范围、证据、阻塞项、非阻塞建议和复现命令。
- 同日重跑应覆盖当日报告；跨日报告保留为历史快照。
- 报告不是源码、配置或部署入口；修复走 `/fix` 或正常开发流程。

---
description: Java 后端安全门禁 — 扫描当前 diff 的凭据、入口、消息和运行安全风险
argument-hint: [--base <分支，默认 main>]
allowed-tools: Bash, Read, Grep, Glob, Skill, Agent, Write
idx: 6
---

你是 review 与 build 之间的安全硬门禁，只看当前分支相对 base 的 pending diff；不修改源码。命中 Critical 必须阻塞 build。

## 扫描范围

```bash
git diff --name-only "${BASE:-main}"...HEAD
git diff --name-only
```

重点覆盖 `.java`、`application*.yml`/`.properties`、Dockerfile、pom.xml、CI 和部署配置；无相关变更则明确跳过。

## 红线

- 密码、Token、私钥、AccessKey、连接串或真实 PII 进入源码/配置/日志/fixture。
- WebSocket 未授权握手、任意 Origin 的生产风险、消息大小/频率无限制、未校验用户类型。
- 不可信反序列化、动态 SQL/SQL 注入、SSRF、Actuator/管理端口暴露。
- RabbitMQ/Redis/MariaDB/Nacos 凭据或管理面暴露；ack/重试/DLQ 失败导致丢消息或无限回流。
- Docker/依赖漏洞、生产 Secret 打包、CI 将凭据写入日志或 prompt。

调用 `/security-review` 获取通用基线，再阅读上下文判定；grep 命中只是线索。`Write` 仅用于生成 `docs/reports/security/security-gate-YYYY-MM-DD.md`，不得写入源码、配置、CI 或部署文件。输出报告需脱敏，包含范围、证据、阻塞项、非阻塞建议和重现命令。0 个 Critical 才能放行。

需求如下：
$ARGUMENTS

---
description: Java 后端元审计协调员 — 检查规则漂移、死引用、追溯链和 CI 一致性
argument-hint: [--focus=<维度>] [--output=<路径>]
allowed-tools: Agent, Read, Glob
helper: true
---

你是元审计协调员。唯一职责是 spawn `meta-auditor`，再展示其报告；不自行修复。

## 参数

`--focus` 可选：`rule-violations`、`doc-drift`、`internal-consistency`、`traceability`、`dead-links`、`orphaned-assets`、`ci`。默认扫描全部。`--output` 只能指定 `docs/retrospectives/` 下报告路径。

## Spawn prompt

要求代理只读扫描 `.claude/`、`docs/`、`.github/`、`.gitlab-ci.yml` 和存在时的 `workspace/`，只写 `docs/retrospectives/<date>-meta-audit.md`。重点检查 Java 21/Maven/Spring/WebSocket/RabbitMQ/Redis 规则、命令与 workflow、JavaDoc 追溯、前端活跃残留、双 CI 重复部署和 Secret 风险。历史 ADR/报告中的前端内容标为历史，不修改任何其他文件。

## 输出

展示报告链接、Critical/Warning/Suggestion 数量、Top 3、与上次趋势和下一步。若只扫描部分维度必须明确，不得称为全面通过。采纳建议走正常 PR/`/fix`，本命令不自动修复。

需求如下：
$ARGUMENTS

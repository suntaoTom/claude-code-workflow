---
description: 任务清单门禁 — 校验 Java 后端任务结构、依赖、契约和追溯
argument-hint: @docs/tasks/<tasks>.json
allowed-tools: Read, Glob, Grep, Bash
helper: true
---

你是任务清单完备性检查器。只读检查，不修改 tasks.json；不通过不得进入 `/code`。

## 第零步：确定性结构检查

先执行 `python3 tools/validate-tasks.py <tasks JSON 路径>`。脚本失败时直接阻塞，不进入后续 AI 依赖、契约和漂移解释。

## 检查项（AI 语义复核）

1. 结构：顶层含 `domain: java-backend`、`moduleCode/prdRef/tasks/createdAt`；每项含 `taskId/type/name/filePath/description/prdRef/businessRules/acceptanceCriteria/dependencies/status`；类型为后端允许集合；ID 唯一，状态为 pending/in-progress/done/blocked。没有 `domain: java-backend` 的历史任务不得进入当前 `/code`。
2. 依赖：无悬挂、无环、无前向引用；依赖方向符合 contract → schema/config → domain/dao/service → controller/handler → tests。
3. 追溯：PRD 文件和每个锚点真实存在；businessRules 来自 PRD 原文且无占位符；协议引用真实。基础设施任务可空 businessRules，但必须有 acceptanceCriteria。
4. 契约：HTTP/WebSocket/RabbitMQ 任务引用真实契约或显式 blocked 的协议任务；消息任务必须覆盖版本、messageId、幂等、失败终态；数据库任务必须有迁移/事务边界。
5. 共享文件：`pom.xml`、application 配置、公共协议、Rabbit topology、migration 顺序和 README 不得被多个任务并行拥有。
6. PRD 未漂移：PRD 当前仍通过 `/prd-check`；PRD 修改晚于 tasks 时警告并建议重跑 `/plan`。

输出 6 项结果、阻塞项文件:行号/任务 ID、软提示和下一步。禁止执行源码、Maven 或部署。

需求如下：
$ARGUMENTS

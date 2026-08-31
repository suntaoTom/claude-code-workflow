# tasks/ — Java 后端任务清单

## 当前任务格式

新生成的任务清单必须在顶层包含：

```json
{
  "domain": "java-backend",
  "moduleCode": "<kebab-case>",
  "prdRef": "docs/prds/<module>.md",
  "tasks": []
}
```

任务类型使用 `contract`、`schema`、`config`、`migration`、`domain`、`dao`、`service`、`controller`、`websocket`、`messaging`、`cache`、`observability`、`security`、`unit-test`、`integration-test`、`contract-test`、`docker`、`ci`、`deploy`、`runbook`、`docs` 等。

状态只能是 `pending`、`in-progress`、`done`、`blocked`。共享 `pom.xml`、Spring 配置、协议、migration 和 README 由主 agent 串行收口。

## 文件清单

| 文件 | 说明 |
|------|------|
| `_template.json` | Java task 结构模板，不参与校验或执行 |

## 历史任务

现有没有 `domain: java-backend` 的旧 JSON（例如早期前端任务）仅作为迁移前历史保留，不参与 `/start`、任务状态 hook 或当前 Java 流程。不要改写、删除或把历史任务伪装成 Java 任务。

## 使用流程

```text
通过 /prd-check 的 PRD
  → /plan 生成带 domain 的 tasks.json
  → /plan-check
  → /code 按依赖实现
  → 任务 status 更新
```

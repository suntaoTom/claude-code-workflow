# hooks/ — Java 后端自动化钩子

> 只做快速提醒，不代替 `/review`、`/security-gate` 或完整 Maven 构建。

## 文件清单

| 文件 | 触发时机 | 作用 |
|------|---------|------|
| [check-hardcode.sh](check-hardcode.sh) | 编辑 Java/POM/YAML/properties 后 | 提醒凭据、连接串、日志敏感信息 |
| [format.sh](format.sh) | 编辑 Java/POM/YAML/properties 后 | 有 Maven 工程时执行 Spotless 检查 |
| [check-tasks-status.sh](check-tasks-status.sh) | 会话开始 | 列出 in-progress 任务 |
| [pre-commit-check.sh](pre-commit-check.sh) | `git commit` 前 | 提醒任务状态和后端关键文件变更 |

## 设计原则

- 默认 `exit 0`，只提醒，不阻断编辑。
- 不输出 Secret 值；扫描命中必须人工阅读上下文。
- 完整 Maven、依赖和集成环境验证交给 `/build`/CI。

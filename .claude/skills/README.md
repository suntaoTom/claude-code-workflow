# skills/ — Claude Code 技能包

> 包形式的扩展技能，负责运行确定性脚本或按需加载参考资料；主流程命令仍放 `commands/`。

## 文件清单

| 技能 | 用途 | 触发场景 |
|------|------|---------|
| [prd-import/](prd-import/) | 非 Markdown 需求导入指引；当前不内置转换器 | Word/Excel/PPT 需先由用户导出/配置转换器后进入 `/prd` |
| [ext-dep-audit/](ext-dep-audit/) | Java/Maven 依赖安全、许可证和健康度 | 依赖巡检/安全扫描 |
| [ext-perf-audit/](ext-perf-audit/) | JVM、SQL、缓存、消息和接口性能审计 | 性能审计/延迟/吞吐/资源分析 |
| [ext-changelog/](ext-changelog/) | 按模块聚合变更影响报告 | 周报/交接/复盘 |

前端专属视觉/a11y skill 已从活跃入口移除；历史文档中的前端术语不代表当前后端流程。

## 命名约定

- `ext-*` 是可选扩展，不是主流程硬依赖。
- 无前缀技能支撑主流程入口（例如 `prd-import`）。
- Skill 中脚本负责拿真实数据，AI 负责解释；安全和部署操作必须有明确授权。

## 目录规范

```text
skills/<skill-name>/
├── SKILL.md
├── scripts/       # 可选，确定性脚本
└── references/    # 可选，按需加载资料
```

新技能需同步更新本 README、相关 docs/WORKFLOW 和触发 description；只读审计技能不直接改源码，修复统一走 `/fix`。

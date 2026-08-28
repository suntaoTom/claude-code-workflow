# agents/ — Java 后端子代理

> 主命令通过 Agent spawn 专项代理；只读代理不修改源码，测试/修复代理只处理被分配的文件。

## 文件清单

| 代理 | 职责 | 被谁 spawn |
|------|------|-----------|
| [test-writer.md](test-writer.md) | 从 JavaDoc `@rules` 生成 JUnit/集成测试 | `/test` |
| [code-reviewer.md](code-reviewer.md) | 只读审查 Java 分层、可靠性、安全和追溯 | `/review` |
| [bug-fixer.md](bug-fixer.md) | 单个已分诊 Java bug 的失败测试与最小修复 | `/fix` |
| [meta-auditor.md](meta-auditor.md) | 扫描规则漂移、死引用和 Maven/Java 追溯链 | `/meta-audit` |

## 并发边界

不同模块且不写同一 Java、配置、协议、migration、README 的任务可以并行；共享文件由主 agent 串行收口。reviewer 和 auditor 只报告，不自行修复。

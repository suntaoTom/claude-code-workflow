---
name: ext-dep-audit
description: Java/Maven 依赖安全与健康度审计，检查漏洞、过时版本、重复依赖和许可证；用户明确要求依赖审计/安全扫描时触发。
---

# ext-dep-audit — Maven 依赖审计

先运行脚本拿确定性数据，再由 AI 解释；不根据记忆猜 CVE 或版本。

```bash
bash .claude/skills/ext-dep-audit/scripts/maven-audit.sh
bash .claude/skills/ext-dep-audit/scripts/maven-outdated.sh
```

审查直接依赖和传递依赖的漏洞、重复版本、废弃组件、许可证、私有仓库来源、scope 是否正确、Spring Boot/Cloud/BOM 对齐、反序列化/日志/数据库客户端风险。当前没有 `workspace/pom.xml` 时明确跳过，不报“通过”。

输出 Critical/High、Medium、Low、需人工确认项和修复命令；major 升级、parent 版本切换和依赖删除只提出建议，不自动执行。

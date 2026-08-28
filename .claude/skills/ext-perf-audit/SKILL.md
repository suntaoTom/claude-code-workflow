---
name: ext-perf-audit
description: Java 后端性能审计，分析 JVM、SQL、Redis、RabbitMQ、WebSocket 和接口延迟；用户明确要求性能审计/延迟/吞吐/资源分析时触发。
---

# ext-perf-audit — Java 后端性能审计

先用脚本拿可复现数据，再做静态分析；不修改业务代码。

## 执行

```bash
bash .claude/skills/ext-perf-audit/scripts/maven-stats.sh
bash .claude/skills/ext-perf-audit/scripts/dependency-tree.sh
```

按 [references/perf-checklist.md](references/perf-checklist.md) 检查：

1. JVM：堆、GC、线程、虚拟线程、连接池和阻塞调用。
2. 数据库：慢 SQL、N+1、索引、分页、事务范围和连接池。
3. Redis：批量访问、TTL、热点 key、序列化和锁等待。
4. RabbitMQ：消费者并发、ack、积压、重试风暴、DLQ 和 Payload 大小。
5. WebSocket：连接数、Session 广播、心跳 sweep、消息限流和单实例路由。
6. API/可观测性：P95/P99、trace、指标、日志开销和健康探针。

只有有测量证据的问题标为严重；没有基准的建议只能列为待测量。输出 file:line、指标、影响、最小修复和验证命令。

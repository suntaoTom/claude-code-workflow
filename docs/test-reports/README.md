# test-reports 目录

> `/test` 产出的 Java 后端验证快照；每次运行独立文件，不覆盖历史。

## 追溯链

```text
PRD → JavaDoc @rules → JUnit @Test/集成测试 → 本目录报告
```

## 命名

`docs/test-reports/<YYYY-MM-DD-HHmm>-<scope>.md`

## 报告必须包含

- JDK/Maven/profile、目标包和外部依赖（MariaDB、Redis、RabbitMQ、Nacos）
- Unit、Spring、DAO/DB、Redis、WebSocket、RabbitMQ、契约/集成分组结果
- `@rules` 原文 → 测试方法 → 状态的规则覆盖矩阵和数值覆盖率
- 按测试代码/环境/预期/源码分诊的失败
- 真实生产、负载、多节点、灾备、证书、第三方鉴权和发布验证人工清单

报告只追加不修改；骨架见 [_template.md](_template.md)。
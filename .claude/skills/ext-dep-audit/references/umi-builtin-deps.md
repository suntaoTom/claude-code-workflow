# Maven 依赖审计参考

## 必查

- Spring Boot/Cloud/Alibaba 与 parent/BOM 版本是否对齐。
- 直接依赖和传递依赖是否重复、多版本共存或来自不可信仓库。
- RabbitMQ、Redis、数据库驱动、序列化和 WebSocket 组件的 CVE、维护状态和许可证。
- 测试依赖 scope 是否正确，生产镜像是否误打入测试依赖。
- 私有 Maven 仓库认证是否来自 CI Secret，不写入 POM。
- `micro-parent` 动态版本范围是否导致不可复现构建；先用 effective POM 记录真实版本。

## 修复边界

安全高危漏洞应升级或隔离；破坏性 major/parent/框架切换必须评估兼容性并走 PRD/ADR。没有 `workspace/pom.xml` 时只报告“待目标工程接入”，不得把工作流仓库当作可构建服务。

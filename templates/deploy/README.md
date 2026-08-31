# 可选 CI/CD 与部署模板

这里存放可复制的宿主平台适配模板，不是默认启用的生产部署配置。

## 目录边界

- `ci/`：GitHub/GitLab Java 验证入口；默认不覆盖目标项目已有 CI。
- `deploy/`：Kubernetes、VM、容器平台的契约和示例；必须在目标项目确认平台、凭据、artifact、健康检查和审批后安装。

母版不保存真实镜像仓库、主机地址、namespace、Secret、Nacos/RabbitMQ/Redis/数据库连接信息。目标项目只能使用固定路径、显式审批和可追溯的 commit/image digest。

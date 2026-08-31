# workspace/ — Java 后端工程插槽

> 本目录是母版仓库中唯一允许放置后端项目代码和运行文件的区域。根目录 `.claude/`、`CLAUDE.md` 和 `docs/` 属于 AI 工作流层，不放业务 Java 源码。

## 接入具体项目后

将目标 Java/Maven 服务放入本目录，预期结构：

```text
workspace/
├── pom.xml
├── mvnw / mvnw.cmd
├── .mvn/
├── src/main/java/<base-package>/
├── src/main/resources/
├── src/test/java/<base-package>/
├── src/test/resources/
├── Dockerfile
└── docs/                 # 仅放服务自身运行/架构文档
```

当前母版不包含业务 Java 代码、POM、Secret、连接串或生产配置；缺少 `pom.xml` 时 `/start`、`/build`、测试和 Maven 辅助脚本必须明确报告“后端项目尚未接入”。

## 运行约定

从仓库根目录启动 Claude Code：

```bash
./tools/backend.sh validate
./tools/backend.sh spotless:check
./tools/backend.sh test
./tools/backend.sh verify
./tools/backend.sh package
./tools/backend.sh run --profile dev
```

脚本始终指向 `workspace/pom.xml`，不会在根目录寻找或执行 Maven 工程。Docker 构建上下文为 `workspace/`。

## 约束

- 不要在 `workspace/` 中创建第二个 `.git`；母版项目推荐单 Git 仓库。
- 不要把外部参考项目复制、绑定或软链接到这里。
- 配置、Token、密码、连接串和生产 Secret 使用 profile/环境变量/Secret 管理注入。
- 后端任务的 `filePath` 统一使用 `workspace/` 前缀；测试统一放 `workspace/src/test/java/`。

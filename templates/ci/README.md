# ci/ — 可选 CI 模板

| 文件 | 说明 |
|------|------|
| `ci-java.yml` | GitHub Java 验证模板，默认不覆盖目标项目 |
| `gitlab-ci.yml` | GitLab Java 模板占位，需填写共享模板和固定版本 |

模板使用 `workspace/` 作为 Maven 工程根目录，安装前确认目标项目已有 `.github`/`.gitlab-ci.yml` 是否需要人工合并。

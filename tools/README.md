# tools/ — 母版辅助工具

| 文件 | 说明 | 退出/结果 |
|------|------|----------|
| `backend.sh` | 从根目录统一调用 `workspace/pom.xml` | 缺少 POM 返回 3 |
| `install-java-backend-workflow.sh` | 安全安装母版，默认不覆盖目标项目 | dry-run 可预览 |
| `validate-prd.py` | 校验 Java PRD 的结构、domain、占位符和引用 | 0 通过，1 阻塞 |
| `validate-tasks.py` | 校验 Java task JSON、依赖图、路径和锚点 | 0 通过，1 阻塞 |
| `check-traceability.py` | 扫描 PRD/task/JavaDoc/测试追溯链 | 0 无错误，1 有错误 |
| `gen_api_md.py` | 从 `docs/contracts/openapi/*.json` 生成接口索引 | 无契约源时明确失败 |

## 使用

```bash
python3 tools/validate-prd.py docs/prds/<module>.md
python3 tools/validate-tasks.py docs/tasks/<tasks>.json
python3 tools/check-traceability.py
./tools/backend.sh validate
```

脚本只依赖 Python 标准库和 Maven/Java 工程已有工具，不创建业务 Java 代码、不写 Secret、不执行生产部署。缺少 `workspace/pom.xml` 时输出未接入状态，不伪造 Maven 通过。

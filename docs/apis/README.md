# 协议层接口文档索引

> 协议层接口的「契约源」, PRD 通过 `@api` 锚点引用具体接口。

## 目录结构

```
docs/
├── contracts/openapi/       # OpenAPI 主源 JSON（后端导出，不手改）
│   └── *.json
└── apis/                    # 由主源生成的人类可读索引
```

## 维护规则

1. **主源**: `../contracts/openapi/*.json` 是事实来源，由后端协议层导出，**不手改**
2. **生成**: 替换 JSON 后执行 `python3 tools/gen_api_md.py` 重新生成本目录 `.md`
3. **业务上下文**: 生成索引不承载人工业务规则；人工说明应放 PRD/ADR
4. **PRD 引用**: `@api docs/apis/<tag-slug>.md#<operation-id>`

## 当前协议源

母版不包含业务 OpenAPI；复制到具体项目后，将后端导出的 JSON 放入 `docs/contracts/openapi/`，再运行生成脚本。

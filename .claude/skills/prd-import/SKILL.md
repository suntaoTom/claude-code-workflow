---
name: prd-import
description: 将 docx/xlsx/pptx 等非 Markdown 需求转换为 PRD 输入素材；当前工作流不自带 Node 转换工程，用户需提供已配置的转换器或先导出为 Markdown。
---

# prd-import — 需求文档格式转换

本 skill 只负责把非 Markdown 需求变成可读的 Markdown 原文，不生成 PRD、不做业务判断、不改 Java 工程。PDF、图片和 Markdown 可直接交给 `/prd` 原生读取。

## 输入与边界

- `.docx/.xlsx/.pptx`：需要用户环境已有对应转换工具；本仓库当前没有 `workspace/` 运行时或转换脚本，不执行不存在的 `pnpm`/Node 入口。
- `.md/.txt`：直接作为 `/prd` 输入。
- `.pdf`/图片：直接 `/prd @<path>`。
- 在线文档：先在平台导出 Markdown 或 Office 文件；不做平台 API 集成。

## 执行流程

1. 检查输入格式和文件是否可读。
2. 若当前仓库没有转换器，明确停止并提供两条路径：用户导出 Markdown；或在目标工程/独立工具中配置转换器后重新运行。
3. 已有转换器时，输出到 `docs/prds/_imports/<basename>-<YYYY-MM-DD>.md`，不覆盖已有文件，并保留源文件路径、格式和转换时间元信息。
4. 读取转换产物，提示 `/prd @<产物>`；复杂表格、图片和合并单元格需人工校对。

## 禁止

- 不凭转换结果推断业务规则、字段、错误码或技术方案；
- 不修改 workspace Java 源码、不写真实凭据；
- 不把转换成功写成 PRD 已通过，仍必须走 `/prd-check`。

详细在线文档导出建议见 [references/formats.md](references/formats.md)。

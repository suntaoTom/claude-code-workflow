# 格式细节与踩坑记录

## .docx (Word 2007+)

### 用的库: [mammoth](https://github.com/mwilliamson/mammoth.js)

- 输出: 用 `convertToMarkdown` API, 保留标题 (H1-H6) / 段落 / 列表 / 表格 / 引用
- 不保留: 字体颜色、字号、图片 (图片被提取但本脚本丢弃)
- 不支持 `.doc` (老格式 OLE 复合文档), 用户请另存为 `.docx`

### 已知限制

| 现象 | 原因 | 解决 |
|------|------|-----|
| 合并单元格错位 | mammoth 把 colspan/rowspan 展开成多个空列 | 人工编辑 md 后修 |
| 脚注丢失 | mammoth 默认不提取脚注 | 如果需求依赖脚注, 手动从原文复制 |
| 页眉页脚丢失 | 不是正文 | 通常不影响需求理解 |
| 嵌入的 Excel 对象被丢弃 | 跨格式嵌入不支持 | 让产品把 Excel 单独导出 |
| 自定义样式被忽略 | mammoth 只识别语义样式 (Heading / List) | 让产品用标准样式写文档 |

### 产品给文档时的建议 (可发给他们)

- 用 Word 自带的 **Heading 1-3** 样式标记标题 (不要手动调字号)
- 表格用规则矩形, 避免合并单元格
- 图片和截图单独放一个目录, 在 Word 里只给文字描述 + 引用编号
- 需求规则用编号列表 (Word 的 List 样式), 不要手动打 "1.", "2."

## .xlsx (Excel 2007+)

### 用的库: [SheetJS xlsx](https://github.com/SheetJS/sheetjs)

- 每个 sheet 转成一段 `## <sheet 名>` 标题 + 一张 markdown 表格
- 空行空列自动去除
- 数字保留原始精度 (不做货币格式化)

### 已知限制

| 现象 | 原因 | 解决 |
|------|------|-----|
| 合并单元格只保留左上角值 | xlsx 的标准行为 | 让产品不要合并 |
| 公式被计算成值 | xlsx 默认策略 | 一般是需求文档不含公式, 不影响 |
| 日期被转成 Excel 序列号 | xlsx 底层存储 | 脚本会检测并转回 ISO 日期字符串 |
| 图表 / 透视表 | 非表格数据 | 不支持, 请让产品出表格版 |

## .pptx (PowerPoint 2007+)

### 做法: 原生 unzip + XML 正则提取

- .pptx 本质是 zip, 内含 `ppt/slides/slide*.xml`
- 脚本解压后用正则抽每个 slide 的文本
- 每张 slide 输出为 `## Slide N` + 文本

### 局限

这是 best-effort, 不是完整转换:

| 丢失内容 | 为什么 |
|---------|-------|
| 布局 / 位置 | 转 md 就没意义了 |
| 图片 / 截图 | 无法 OCR |
| 动画 / 过渡 | 无法表达 |
| 演讲者备注 | 默认不抽 (如需要改脚本读 `notesSlide*.xml`) |

**建议**: 如果需求主要靠 PPT 表达, 让产品补一个 Word 或 markdown 版, PPT 作为辅助。

## .pdf

**不走本 skill**。Claude Code 的 `Read` 工具原生支持 PDF (带 `pages` 参数读指定页), 视觉模型能识别扫描件。直接:

```bash
/prd @requirements/登录需求.pdf
```

`/prd` 内部会读 PDF 内容, 和读 md 一样。

**例外**: 如果 PDF 超过 20 页, `Read` 要求指定 pages 范围。这时:
1. 先用 PDF 阅读器看一下目录, 找关键章节页码
2. 分段读 `@<file.pdf>` pages="1-10" 之类

## 图片需求 (.png / .jpg / .jpeg)

**不走本 skill**。Claude Code 多模态能力会识别需求截图、流程图、原型图。直接:

```bash
/prd @requirements/登录流程.png
```

## 其他格式

| 格式 | 建议 |
|------|------|
| `.md` / `.txt` | 直接 `/prd @<file>`, 不必转换 |
| Notion 导出 `.md` + `_imports/` | 用 Notion 的 "Export as Markdown" (会带图片), 直接喂 `/prd` |
| 飞书 / 语雀 导出 `.docx` | 当普通 docx 处理 |
| Confluence 导出 `.html` | 目前没支持, 可手动复制内容到 .md |
| 钉钉文档 / 腾讯文档 | 导出为 .docx 再走本 skill |

## 字符编码

脚本默认用 UTF-8 读写。如果源文件是 GBK / GB18030 (老版 Windows Word 偶尔出现):
- mammoth 自己处理 docx 内部编码, 不受影响
- xlsx 同上
- 纯 .txt 文件如果是 GBK, 脚本会输出警告并尝试 `iconv-lite` 转换 (如果装了)

如果转出来全是乱码, 让用户用 VSCode 打开源文件, 右下角切编码为 UTF-8 另存即可。

---

## 在线文档怎么办

产品常用**飞书 / Notion / 语雀 / 腾讯文档 / Google Docs** 等在线平台写需求。本 skill **不做任何平台 API 集成**, 请走以下路径之一。

### 路径 1 (推荐): 导出到本地再走 prd-import

每个平台都有导出功能, 找对位置即可:

| 平台 | 导出路径 | 推荐格式 | 产出质量 |
|------|---------|---------|---------|
| **飞书文档** | 右上角 `···` 更多 → 导出为 Word | `.docx` | 好 (表格结构完整) |
| **Notion** | `Share` → `Export` → `Markdown & CSV` | `.md` ⭐ 直接用 | 极好 (Notion 原生 md) |
| **语雀** | 更多 `···` → 导出 → Markdown | `.md` ⭐ 直接用 | 好 (语雀原生 md) |
| **腾讯文档** | 文件 → 导出为 → Word | `.docx` | 一般 (表格偶尔错位) |
| **Google Docs** | File → Download → Microsoft Word (.docx) | `.docx` | 好 |
| **Confluence** | `···` → Export → Word Document | `.docx` | 好 |
| **钉钉文档** | 更多 → 导出 → Word | `.docx` | 一般 |
| **石墨文档** | 右上角 `···` → 导出 → Word | `.docx` | 一般 |
| **Microsoft OneNote/Word Online** | File → Export → .docx | `.docx` | 好 |

**关键提示**:
- 有 `.md` 导出的平台 (Notion / 语雀) **直接跑 `/prd @<文件.md>` 即可**, 连 prd-import 都不用
- 其他平台导出 `.docx` 后, 跑 `pnpm prd:import <file.docx>` 再 `/prd @<产物>`

**操作示例** (飞书为例):

```
1. 产品在飞书给你发了需求文档链接
2. 打开链接, 右上角 ··· → 导出 → Word
3. 下载到本地 (假设叫 登录需求.docx)
4. 本地命令:
   pnpm prd:import 登录需求.docx
   → docs/prds/_imports/登录需求-2026-04-20.md
5. /prd @docs/prds/_imports/登录需求-2026-04-20.md
```

### 路径 2 (进阶, 用户自配): MCP

Claude Code 支持 [Model Context Protocol](https://docs.claude.com/en/docs/claude-code/mcp), 用 MCP server 可以让 AI 直接读在线文档, 不用手动导出。

**项目不内置 MCP 配置**, 用户在 `~/.claude/mcp.json` 自己配, 配好后 `/prd` 能通过工具访问在线内容。

可用的 MCP server:

| 平台 | MCP server | 配置复杂度 |
|------|-----------|-----------|
| **Notion** | [`@notionhq/notion-mcp-server`](https://github.com/makenotion/notion-mcp-server) | ⭐⭐ (要建 integration, 拿 secret) |
| **Google Drive** | Anthropic 官方 Google Drive MCP | ⭐⭐ (OAuth, 一次授权) |
| **飞书 / 语雀 / 腾讯 / 钉钉** | 社区零星有, 质量不一 | ⭐⭐⭐ 自担风险 |

**什么时候值得配 MCP**:
- 团队 80% 需求都在某一个平台 (比如 Notion 深度用户)
- 需求经常迭代, 手动导出频率高
- 有授权体系, 能一次配置长期用

**什么时候别配**:
- 一周见一次在线文档 → 手动导出更划算
- 平台不在上表 → 自己写 MCP 得不偿失
- 文档敏感 (客户 / 财务 / HR) → 不要让 AI 拿 token

### 路径 3 (不推荐): 让 AI 抓链接

部分平台支持公开分享链接, 理论上可以 `curl` 拿 HTML 再解析。**项目不提供这个能力**, 因为:
- 大多数团队内部文档不是公开分享状态
- HTML 解析脆弱, 各家 DOM 一改就挂
- 维护成本高, 收益低

如果你真的需要一次性抓某个公开 URL, 用浏览器的「另存为完整网页 → HTML」然后手动贴文本, 不要期待 AI 自动化。

### 为什么不自己做 API 集成

详见 [docs/DECISIONS.md](../../../../docs/DECISIONS.md) 对应条目。简要:
- 每家 (飞书/Notion/语雀/Google) 认证机制完全不同, token 刷新 / 权限 / rate limit 全是活
- 平台改版就挂, 框架从"工具"变成"运维项目"
- 90% 的团队只用 1-2 家, 做全了浪费
- 路径 1 (导出) 3 分钟就能覆盖所有平台

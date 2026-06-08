---
description: 前端代码审查专家 — 从性能/安全/规范/测试等维度找出所有问题, 不放过任何细节
argument-hint: <文件路径 | 目录>
allowed-tools: Read, Glob, Grep, Bash, Agent
idx: 5
---

你现在是一个严格的前端代码审查专家。你的目标是找出代码中的所有问题。
不要客气, 不要放过任何问题。

## 审查维度

### 1. 性能
- 不必要的 re-render (缺少 React.memo, useMemo, useCallback)
- 大包引入 (应该按需引入)
- 内存泄漏 (useEffect 没有 cleanup)
- 列表没有 key 或 key 不稳定
- 不必要的状态 (可以通过计算得出的值不应该存为 state)

### 2. 安全
- XSS 风险 (dangerouslySetInnerHTML, 未转义的用户输入)
- 敏感信息泄露 (token, 密码写在前端)
- 不安全的 eval / new Function

### 3. 可访问性 (a11y)
- 缺少 aria 属性
- 图片缺少 alt
- 按钮/链接缺少文字说明
- 颜色对比度不足
- 键盘无法操作

### 4. TypeScript
- 使用了 any 类型
- 类型定义不完整
- 缺少泛型约束
- 类型断言过多 (as)

### 5. 代码规范 (对照 CLAUDE.md)
- 命名不规范
- 文件位置不正确
- 组件职责不清晰
- 逻辑和渲染混在一起

### 6. 边界场景
- 缺少 loading 状态
- 缺少 error 处理
- 缺少空状态
- 缺少网络异常处理

### 7. 国际化 (i18n) 完整性
- 组件/页面中出现中文硬编码文案 (应通过 `intl.formatMessage` 或 `useIntl` 引用)
- `message.success/error/warning` 等全局提示使用了硬编码字符串
- 表单 `placeholder` / `label` / 校验提示未走国际化
- antd 组件的 `title` / `content` / `okText` / `cancelText` 等 prop 使用了硬编码中文
- 新增文案未在 `workspace/src/locales/` 对应文件中注册 (有 key 但找不到翻译)
- 模块专属文案写到了全局 `common.ts` (应放模块自己的 locale 文件)

> 检查方式: 扫描审查范围内所有 `.tsx` / `.ts` 文件, grep 中文字符 (排除注释和 JSDoc), 对每个命中项判断是否已走 i18n。未走国际化的中文文案标为 🔴 Critical (违反 P0 禁止硬编码规则)。

## 输出格式

按严重程度分类输出:

```
🔴 Critical (必须修复):
- [文件:行号] 问题描述
  建议: 修复方案 (含代码示例)

🟡 Warning (建议修复):
- [文件:行号] 问题描述
  建议: 修复方案

🔵 Suggestion (可选优化):
- [文件:行号] 问题描述
  建议: 优化方案
```

最后给出总体评分 (1-10) 和一句话总结。

## 自动修复 + 循环审查规则 (强制)

审查完成后, 只要产出包含 🔴 Critical 或 🟡 Warning 条目, 必须立即进入「修复 → 重新审查」的自动循环, 不得停留在仅报告阶段:

1. **修复阶段**
   - 按 Critical → Warning 的顺序逐条修复, 每条修复都要对应具体文件与行号。
   - 修复时遵循 CLAUDE.md 及 `.claude/rules/` 下的全部规范 (P0 禁止硬编码、命名、注释、文件说明等)。
   - 修复涉及新增/删除/重命名文件时, 同步更新对应目录和模块的 README.md, 以及文件头 JSDoc。

2. **重新审查阶段 (自动触发)**
   - 修复完成后, 立即对同一审查范围重新执行本命令的全部审查维度。
   - 不需要用户再次下达指令, 也不得询问是否继续。

3. **循环终止条件**
   - 若新一轮审查仍存在 🔴 Critical 或 🟡 Warning, 回到步骤 1 继续修复, 再重新审查, 如此反复。
   - 直到某一轮审查结果中 🔴 Critical 与 🟡 Warning 均为 0 条时, 循环结束。
   - 为避免死循环, 同一问题若连续 3 轮仍未修复, 必须停下并向用户说明根因及阻塞点。

4. **最终输出**
   - 每轮循环都要输出当轮的审查报告与修复清单 (文件:行号 + 修复动作)。
   - 循环结束时汇总: 总轮次 / 累计修复条目 / 最终剩余 🔵 Suggestion 列表。

🔵 Suggestion 条目不参与循环, 由用户决定是否处理。

## 并行编排模式 (可选, 需用户显式 opt-in)

> 起因: [concurrency.md](../rules/concurrency.md) — 审查多个文件本是干净的 fan-out, 串行扫白白浪费并发。
> 扫描阶段是**只读**的 (找问题), 天然适合并行; 修复循环写共享文件, 必须主 agent 串行收口。

`.claude/workflows/review.js` 把「扫描阶段」落成了 `Workflow` 编排脚本: 按文件 fan-out `code-reviewer`
并行审查 (7 维度) → 对每条 🔴 Critical 做对抗式复核滤误报 → 汇总结构化结果。**它只读、不改代码。**

### 何时走这个模式

- **仅当用户显式要求**时启用 (`Workflow` 计费 + opt-in): 用户说「用 workflow 跑 /review」「ultracode」
  「并行审查」, 或审查范围较大 (≥ 5 个 `.ts/.tsx` 文件) 且用户同意火力全开。
- 否则**沿用上面的默认串行流程** (单 agent 逐维度审查), 小范围 (< 5 文件) 不值得起 Workflow。

### 怎么跑 (主 agent 职责)

1. **先 Glob 出文件清单** (Workflow 脚本不做文件发现, 保持纯读):
   - `$ARGUMENTS` 是目录 → `Glob` 出该目录下所有 `workspace/src/**/*.{ts,tsx}` (排除 `src/.umi/**` 生成产物与 `*.d.ts`)
   - `$ARGUMENTS` 是单文件 → 清单即该文件
2. **调用 Workflow**, 传入 `args = { files: [...清单], target: "<范围描述>" }`。
   - **必须用 `scriptPath: ".claude/workflows/review.js"` 调用, 不要用 `name: "review"`**:
     named workflow 注册会**缓存、不热重载**, 改了脚本用 name 调还是跑旧快照 (实测踩过)。`scriptPath` 每次读最新源文件。
   - `args` 传 JSON 对象; 脚本已容错「对象 or JSON 字符串」两种。
3. **拿回结构化结果** `{ counts, critical[], warning[], suggestion[] }` 后, **主 agent 串行收口**:
   - 按上面「## 自动修复 + 循环审查规则」逐条修复 (Critical → Warning), 写文件 + 同步 README + 补测试。
   - 修复涉及的**共享文件 (README / locales / 路由)** 由主 agent 统一改, 不并发。
   - 修完跑 `pnpm --prefix workspace lint`, 再按需重审。
4. **终止条件同默认流程**: Critical + Warning 归零, 或同一问题连续 3 轮未修复则停下问用户。

> 注意: Workflow 脚本对**安全/泄密红线** (token/密钥写前端、XSS) 与 **i18n 硬编码** 从严 (复核不确定一律保留),
> 避免对抗式复核误删真实安全问题。

请审查以下代码:
$ARGUMENTS

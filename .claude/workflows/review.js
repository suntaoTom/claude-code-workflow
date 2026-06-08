export const meta = {
  name: 'review',
  description: '前端代码审查 — 按文件 fan-out code-reviewer 对照项目规则多维度审查, 对每条 Critical 发现做对抗式复核滤误报, 汇总成结构化报告 (只读, 不改代码)',
  phases: [
    { title: 'Scan', detail: '每个 .ts/.tsx 文件一个 code-reviewer, 对照 7 维度规则并行审查' },
    { title: 'Verify', detail: '对每条 Critical 发现独立复核, 滤掉误报 (安全/泄密相关从严保留)' },
    { title: 'Synthesize', detail: '汇总去重, 按严重度统计, 产出报告数据交主 agent 收口' },
  ],
}

// ── 入参契约 ──────────────────────────────────────────────────────────────
// args.files: string[]  待审查的 .ts/.tsx 路径列表 (由命令层先 Glob 出来再传入)
// args.target: string   本次审查范围的人类可读描述 (例: src/pages/order), 仅用于报告标题
// 设计原则: 文件发现 (Glob) 由主 agent 在调用前完成, Workflow 只负责「拿到清单后并行审查」,
//          这样 Workflow 保持纯读、无 fs 依赖, 也契合 concurrency.md「共享文件主 agent 收口」。
let parsedArgs = args
if (typeof parsedArgs === 'string') {
  try { parsedArgs = JSON.parse(parsedArgs) } catch (e) { parsedArgs = {} }
}
const files = (parsedArgs && Array.isArray(parsedArgs.files)) ? parsedArgs.files : []
const target = (parsedArgs && parsedArgs.target) || '(未指定范围)'

if (!files.length) {
  log(`⚠️ args.files 为空 (typeof args=${typeof args}) — 请由命令层先 Glob 出待审查的 .ts/.tsx 文件再传入 args.files`)
  return { error: 'no_files', target, files: 0, findings: [] }
}

log(`审查范围: ${target} — 共 ${files.length} 个文件`)

// ── 审查维度 (与 .claude/commands/review.md 的 7 维度一致, 浓缩版) ──────────
const DIMENSIONS = `审查必须对照项目规则文件 (请先 Read 这些文件再审):
- .claude/rules/coding-style.md  命名/组件职责/Hooks/状态/异步/规范
- .claude/rules/no-hardcode.md   P0 禁止硬编码 (文案/颜色/配置, 违反一律 critical)
- .claude/rules/file-docs.md     文件头 JSDoc + README 同步
- .claude/rules/testing.md       业务规则 ↔ 测试用例对应
- .claude/rules/tech-stack.md    技术栈 (UmiJS + React + TS + antd) 与目录结构

按以下 7 个维度逐一检查:
1. 性能: 不必要 re-render (缺 React.memo/useMemo/useCallback); 大包全量引入 (应按需); useEffect 缺 cleanup 致内存泄漏; 列表无 key 或 key 不稳; 可计算值却存成 state
2. 安全: XSS (dangerouslySetInnerHTML / 未转义用户输入); 敏感信息 (token/密钥/密码) 写在前端或提交进代码/config; 不安全的 eval / new Function
3. 可访问性: 缺 aria 属性; 图片缺 alt; 按钮/链接缺文字; 颜色对比度不足; 键盘无法操作
4. TypeScript: 出现 any; 类型定义不完整; 缺泛型约束; 滥用 as 类型断言
5. 代码规范: 命名不规范 (组件 PascalCase 等); 文件位置不对; 组件职责不清; 逻辑与渲染混在一起
6. 边界场景: 缺 loading / error / 空状态 / 网络异常处理
7. i18n 完整性 (违反一律 critical): 中文硬编码未走 intl.formatMessage/useIntl; message.success/error 硬编码; 表单 placeholder/label/校验提示未国际化; antd 组件 title/content/okText/cancelText 等 prop 硬编码中文; 新增文案未在 workspace/src/locales/ 注册; 模块文案错放全局 common.ts

注意 (例外, 不要误判):
- 跳过 Umi 生成产物 (workspace/src/.umi/**) 与 *.d.ts 声明文件, 它们非手写源码。
- 注释 / JSDoc 里的中文不算硬编码文案。`

const FINDINGS_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['findings'],
  properties: {
    findings: {
      type: 'array',
      items: {
        type: 'object',
        additionalProperties: false,
        required: ['severity', 'dimension', 'line', 'issue', 'suggestion'],
        properties: {
          severity: { type: 'string', enum: ['critical', 'warning', 'suggestion'] },
          dimension: { type: 'string', description: '所属维度, 如 "2 安全" / "7 i18n"' },
          line: { type: ['integer', 'null'], description: '问题所在行号, 无法定位填 null' },
          issue: { type: 'string', description: '问题描述' },
          suggestion: { type: 'string', description: '修复建议, 可含代码示例' },
        },
      },
    },
  },
}

const VERDICT_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['isReal', 'reason'],
  properties: {
    isReal: { type: 'boolean', description: '该 Critical 是否为真问题。安全/泄密相关从严: 只有高度确信是误报才填 false, 任何不确定一律 true' },
    reason: { type: 'string', description: '判定理由 (引用文件内容或规则原文)' },
  },
}

const short = (f) => f.split('/').slice(-2).join('/')

// ── Scan + Verify 流水线 (pipeline: 每个文件审完即刻复核, 不等其他文件) ───────
phase('Scan')
const perFile = await pipeline(
  files,
  // stage 1: 审查单个文件
  (file) => agent(
    `你是严格的前端 (React + TypeScript + UmiJS) 代码审查专家。审查这一个文件: ${file}\n\n` +
    `${DIMENSIONS}\n\n` +
    `请先 Read 上述规则文件和目标文件本身, 然后逐维度找出所有问题。不要客气, 不放过任何问题。` +
    `只报告 ${file} 这一个文件内的问题, 不要扩散到其他文件。每条给出 severity / dimension / line / issue / suggestion。`,
    { label: `scan:${short(file)}`, phase: 'Scan', schema: FINDINGS_SCHEMA, agentType: 'code-reviewer' },
  ),
  // stage 2: 对该文件的每条 Critical 做对抗式复核
  (review, file) => {
    const all = (review && review.findings) || []
    const crits = all.filter((f) => f.severity === 'critical')
    const others = all.filter((f) => f.severity !== 'critical')
    if (!crits.length) return { file, findings: all }
    return parallel(
      crits.map((c) => () =>
        agent(
          `对抗式复核。文件 ${file} 第 ${c.line} 行被某审查员判为 🔴 Critical:\n` +
          `维度: ${c.dimension}\n问题: ${c.issue}\n\n` +
          `请重新 Read 该文件确认这是不是真问题。倾向于反驳 (默认怀疑). ` +
          `但安全/泄密红线 (XSS、token/密钥写前端、eval) 与 i18n 硬编码从严: 只有当你高度确信这是误报时才判 isReal=false, ` +
          `任何不确定一律 isReal=true 保留。`,
          { label: `verify:${short(file)}`, phase: 'Verify', schema: VERDICT_SCHEMA },
        ).then((v) => ({ ...c, verdict: v })),
      ),
    ).then((verified) => {
      const keptCrits = verified
        .filter(Boolean)
        .filter((c) => !c.verdict || c.verdict.isReal !== false)
        .map((c) => ({ ...c, verifyReason: c.verdict ? c.verdict.reason : '' }))
      const dropped = verified.filter(Boolean).filter((c) => c.verdict && c.verdict.isReal === false)
      if (dropped.length) log(`${short(file)}: 复核滤掉 ${dropped.length} 条误报 Critical`)
      return { file, findings: [...keptCrits, ...others] }
    })
  },
)

// ── 汇总 (主 agent 收口前的结构化结果) ──────────────────────────────────────
phase('Synthesize')
const allFindings = perFile
  .filter(Boolean)
  .flatMap((r) => (r.findings || []).map((f) => ({ ...f, file: r.file })))

const bySeverity = (sev) => allFindings.filter((f) => f.severity === sev)
const critical = bySeverity('critical')
const warning = bySeverity('warning')
const suggestion = bySeverity('suggestion')

log(`审查完成: 🔴 ${critical.length}  🟡 ${warning.length}  🔵 ${suggestion.length}`)

return {
  target,
  files: files.length,
  counts: { critical: critical.length, warning: warning.length, suggestion: suggestion.length },
  critical,
  warning,
  suggestion,
}

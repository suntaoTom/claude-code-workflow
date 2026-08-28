export const meta = {
  name: 'review',
  description: 'Java 后端代码审查：按文件并行检查分层、协议、可靠性、安全和追溯链，只读汇总',
  phases: [
    { title: 'Scan', detail: '每个 Java/POM/配置文件由 code-reviewer 独立审查' },
    { title: 'Verify', detail: '对 Critical 发现做独立证据复核' },
    { title: 'Synthesize', detail: '去重并按严重度汇总给主 agent 收口' },
  ],
}

let parsedArgs = args
if (typeof parsedArgs === 'string') {
  try { parsedArgs = JSON.parse(parsedArgs) } catch (error) { parsedArgs = {} }
}
const files = parsedArgs && Array.isArray(parsedArgs.files) ? parsedArgs.files : []
const target = parsedArgs && parsedArgs.target ? parsedArgs.target : '(未指定范围)'
if (!files.length) {
  log('⚠️ args.files 为空，请由命令层先 Glob 出 Java/POM/配置文件')
  return { error: 'no_files', target, files: 0, findings: [] }
}

const DIMENSIONS = `请先读取 .claude/rules/tech-stack.md、coding-style.md、no-hardcode.md、file-docs.md、testing.md、reliability.md、security.md。
逐项检查：
1. Java 分层、依赖方向、构造器注入、DTO/Form/BO/DO/VO 边界、事务和异常；
2. SQL/索引/N+1、缓存、线程池、定时任务、资源释放；
3. WebSocket 握手身份、Origin、连接/消息限制、心跳、超时、关闭幂等和多实例前提；
4. RabbitMQ messageId/idempotency/correlation/trace、Confirm/Return、Inbox/Outbox、ack、重试、退避、DLQ、消息版本；
5. 配置外置、日志脱敏、反序列化、动态 SQL、SSRF、Actuator、容器和依赖安全；
6. JavaDoc @prd/@task/@api/@rules、README、JUnit 与 Spotless。
只报告有证据的问题，必须给 file:line、severity、规则来源和建议。`

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
          dimension: { type: 'string' },
          line: { type: ['integer', 'null'] },
          issue: { type: 'string' },
          suggestion: { type: 'string' },
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
    isReal: { type: 'boolean' },
    reason: { type: 'string' },
  },
}
const short = (file) => file.split('/').slice(-2).join('/')

phase('Scan')
const perFile = await pipeline(
  files,
  (file) => agent(
    `你是只读 Java 后端审查员。目标文件：${file}\n\n${DIMENSIONS}`,
    { label: `scan:${short(file)}`, phase: 'Scan', schema: FINDINGS_SCHEMA, agentType: 'code-reviewer' },
  ),
  (review, file) => {
    const findings = review && Array.isArray(review.findings) ? review.findings : []
    const critical = findings.filter((finding) => finding.severity === 'critical')
    const others = findings.filter((finding) => finding.severity !== 'critical')
    if (!critical.length) return { file, findings }
    return parallel(critical.map((finding) => () => agent(
      `独立复核 Java 后端审查发现。文件：${file}，第 ${finding.line} 行，维度：${finding.dimension}，问题：${finding.issue}。\n请读取文件和相关规则，默认怀疑但对凭据、授权、消息丢失和数据破坏风险从严保留。返回 isReal 和证据理由。`,
      { label: `verify:${short(file)}`, phase: 'Verify', schema: VERDICT_SCHEMA },
    ).then((verdict) => ({ ...finding, verdict })))).then((verified) => ({
      file,
      findings: [
        ...verified.filter((finding) => !finding.verdict || finding.verdict.isReal).map((finding) => ({ ...finding, verifyReason: finding.verdict.reason })),
        ...others,
      ],
    }))
  },
)

phase('Synthesize')
const allFindings = perFile.filter(Boolean).flatMap((result) => (result.findings || []).map((finding) => ({ ...finding, file: result.file })))
const bySeverity = (severity) => allFindings.filter((finding) => finding.severity === severity)
const critical = bySeverity('critical')
const warning = bySeverity('warning')
const suggestion = bySeverity('suggestion')
log(`审查完成：🔴 ${critical.length}  🟡 ${warning.length}  🔵 ${suggestion.length}`)
return {
  target,
  files: files.length,
  counts: { critical: critical.length, warning: warning.length, suggestion: suggestion.length },
  critical,
  warning,
  suggestion,
}

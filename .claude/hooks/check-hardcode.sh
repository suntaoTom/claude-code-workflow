#!/bin/bash
# Java/POM/YAML 硬编码快速检查；PostToolUse 触发，只提醒不阻断。
filepath="$CLAUDE_FILE_PATH"
[ -z "$filepath" ] || [ ! -f "$filepath" ] && exit 0
case "$filepath" in
  *.java|*.yml|*.yaml|*.properties|*/pom.xml) ;;
  *) exit 0 ;;
esac
match_lines=$(grep -nE '(password|secret|private.?key|access.?key)[[:space:]]*[:=][[:space:]]*[^${<][^ ]+|jdbc:[^${<]|redis://[^${<]|amqp://[^${<]' "$filepath" 2>/dev/null | grep -vE '(example|placeholder|CHANGE_ME|\$\{|<[^>]+>)' | cut -d: -f1 | head -5)
if [ -n "$match_lines" ]; then
  echo "⚠️ P0 硬编码检测: $filepath 可能包含凭据或连接信息，请改用 profile/Secret/环境变量"
  echo "  可疑行号: $match_lines"
fi
log_lines=$(grep -nE 'System\.out|printStackTrace|log\.(trace|debug|info|warn|error).*([Pp]ayload|[Pp]assword|[Tt]oken|[Cc]ookie)' "$filepath" 2>/dev/null | cut -d: -f1 | head -5)
if [ -n "$log_lines" ]; then
  echo "⚠️ 日志安全检测: $filepath 可能输出敏感信息或完整 Payload"
  echo "  可疑行号: $log_lines"
fi
exit 0

#!/bin/bash
# 提交前提醒：任务状态、Java 构建关键文件和敏感文件。
# 触发时机：PreToolUse（Bash，仅 git commit 命令）；只提醒，不阻断。
echo "$CLAUDE_TOOL_INPUT" | grep -q 'git commit' || exit 0
root="$(cd "$(dirname "$0")/../.." && pwd)"

for file in "$root"/docs/tasks/tasks-*.json; do
  [ -f "$file" ] || continue
  grep -Eq '"domain"[[:space:]]*:[[:space:]]*"java-backend"' "$file" || continue
  if grep -Eq '"status"[[:space:]]*:[[:space:]]*"(in-progress|blocked)"' "$file"; then
    echo "⚠️ 提交前检查: $(basename "$file") 仍有 in-progress/blocked 任务，请确认状态和阻塞原因"
  fi
done

changed=$(git -C "$root" diff --cached --name-only 2>/dev/null)
if printf '%s\n' "$changed" | grep -Eq '(^|/)(application[^/]*\.(yml|yaml|properties)|.*\.(pem|key)|Dockerfile|pom.xml)$'; then
  echo "ℹ️ 提交前检查: 本次包含 Java 构建/运行配置，请确认无真实凭据且 profile/Secret 外置"
fi
exit 0

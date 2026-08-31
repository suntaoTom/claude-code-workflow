#!/bin/bash
# 未完成任务提醒: 开启会话时扫描 in-progress 任务
# 触发时机: ConversationStart

PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
found=0

for f in "$PROJECT_ROOT"/docs/tasks/tasks-*.json; do
  [ -f "$f" ] || continue
  grep -Eq '"domain"[[:space:]]*:[[:space:]]*"java-backend"' "$f" || continue

  if grep -Eq '"status"[[:space:]]*:[[:space:]]*"in-progress"' "$f" 2>/dev/null; then
    if [ $found -eq 0 ]; then
      echo "📋 发现未完成的 Java 后端任务:"
      found=1
    fi
    tasks=$(awk '
      /"taskId"[[:space:]]*:/ { task=$0 }
      /"status"[[:space:]]*:[[:space:]]*"in-progress"/ { print task }
    ' "$f" \
      | sed -nE 's/.*"taskId"[[:space:]]*:[[:space:]]*"([^"]+)".*/\1/p' \
      | tr '\n' ' ')
    basename=$(basename "$f")
    echo "  $basename: $tasks"
  fi
done

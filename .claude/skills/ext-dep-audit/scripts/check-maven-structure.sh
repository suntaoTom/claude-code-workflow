#!/usr/bin/env bash
# check-maven-structure.sh — 检查 Maven 工程关键结构和配置风险
set -u
ROOT="$(cd "$(dirname "$0")/../../../.." && pwd)"
PROJECT="$ROOT/workspace"
if [ ! -f "$PROJECT/pom.xml" ]; then
  echo "ℹ️ workspace/pom.xml 不存在，跳过 Maven 结构检查"
  exit 0
fi
printf '%s\n' '===== Maven structure ====='
for path in src/main/java src/main/resources src/test/java src/test/resources; do
  if [ -d "$PROJECT/$path" ]; then echo "✅ $path"; else echo "⚠️ 缺少 $path"; fi
done
printf '%s\n' '===== Sensitive configuration clues ====='
grep -RInE '(password|secret|private.?key|access.?key)\s*:' "$PROJECT/src" --include='*.yml' --include='*.yaml' --include='*.properties' 2>/dev/null | grep -vE '(\$\{|CHANGE_ME|example)' | head -20 || true

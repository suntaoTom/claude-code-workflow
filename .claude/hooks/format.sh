#!/bin/bash
# Java 文件修改后执行轻量格式检查；PostToolUse 触发，不自动覆盖业务代码。
filepath="$CLAUDE_FILE_PATH"
[ -z "$filepath" ] || [ ! -f "$filepath" ] && exit 0
case "$filepath" in
  *.java|*/pom.xml|*.yml|*.yaml|*.properties) ;;
  *) exit 0 ;;
esac
root="$(cd "$(dirname "$0")/../.." && pwd)"
if [ -f "$root/workspace/pom.xml" ]; then
  (cd "$root/workspace" && mvn -B -ntp -q spotless:check -Dspotless.check.skip=false) >/dev/null 2>&1 || echo "⚠️ Spotless 检查未通过或 Maven 工程尚未就绪，请在 /build 前处理"
fi
exit 0

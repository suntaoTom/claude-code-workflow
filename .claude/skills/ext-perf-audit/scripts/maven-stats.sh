#!/usr/bin/env bash
# maven-stats.sh — 输出 Java/Maven 构建和测试产物的可测量信息
set -u
ROOT="$(cd "$(dirname "$0")/../../../.." && pwd)"
PROJECT="$ROOT/workspace"
if [ ! -f "$PROJECT/pom.xml" ]; then
  echo "ℹ️ workspace/pom.xml 不存在，当前工作流仓库没有 Java 示例服务"
  exit 0
fi
printf '%s\n' '===== Maven/JDK ====='
java -version 2>&1 | head -3
mvn -version 2>&1 | head -4
printf '%s\n' '===== Target size ====='
if [ -d "$PROJECT/target" ]; then du -sh "$PROJECT/target"; find "$PROJECT/target" -type f -name '*.jar' -exec ls -lh {} \;
else echo 'target/ 不存在，请先运行 mvn package'; fi
printf '%s\n' '===== Test reports ====='
find "$PROJECT/target" -type f -path '*surefire-reports/*' 2>/dev/null | wc -l | awk '{print "  report files: " $1}'

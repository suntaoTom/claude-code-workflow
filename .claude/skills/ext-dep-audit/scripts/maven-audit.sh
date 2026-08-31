#!/usr/bin/env bash
# maven-audit.sh — 输出 Maven 依赖树并尝试 OWASP 依赖检查
set -u
ROOT="$(cd "$(dirname "$0")/../../../.." && pwd)"
PROJECT="$ROOT/workspace"
if [ ! -f "$PROJECT/pom.xml" ]; then
  echo "ℹ️ workspace/pom.xml 不存在，跳过 Maven 依赖审计"
  exit 0
fi
mvn -f "$PROJECT/pom.xml" -B -ntp dependency:tree 2>&1
if grep -q 'dependency-check' "$PROJECT/pom.xml" 2>/dev/null; then
  mvn -f "$PROJECT/pom.xml" -B -ntp org.owasp:dependency-check-maven:check 2>&1 || true
else
  echo "ℹ️ POM 未声明 OWASP Dependency-Check；请在 CI 安全流水线执行依赖扫描"
fi

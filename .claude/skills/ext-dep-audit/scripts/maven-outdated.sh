#!/usr/bin/env bash
# maven-outdated.sh — 输出 Maven 依赖更新信息
set -u
ROOT="$(cd "$(dirname "$0")/../../../.." && pwd)"
PROJECT="$ROOT/workspace"
if [ ! -f "$PROJECT/pom.xml" ]; then
  echo "ℹ️ workspace/pom.xml 不存在，跳过 Maven 依赖更新检查"
  exit 0
fi
mvn -f "$PROJECT/pom.xml" -B -ntp versions:display-dependency-updates versions:display-parent-updates 2>&1 || true

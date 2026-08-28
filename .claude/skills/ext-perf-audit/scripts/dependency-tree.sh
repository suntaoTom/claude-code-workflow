#!/usr/bin/env bash
# dependency-tree.sh — 输出 Maven 依赖树，供依赖体积/重复版本分析
set -u
ROOT="$(cd "$(dirname "$0")/../../../.." && pwd)"
PROJECT="$ROOT/workspace"
if [ ! -f "$PROJECT/pom.xml" ]; then
  echo "ℹ️ workspace/pom.xml 不存在，跳过 Maven 依赖分析"
  exit 0
fi
(cd "$PROJECT" && mvn -B -ntp dependency:tree -DoutputType=text) 2>&1

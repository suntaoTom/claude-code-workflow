#!/usr/bin/env bash
# changed-files.sh — 列出指定范围内变更的文件 (A/M/D)
# 用法: bash .claude/skills/ext-changelog/scripts/changed-files.sh [since] [scope]

set -u

SINCE="${1:-7 days ago}"
SCOPE="${2:-.}"

ROOT="$(cd "$(dirname "$0")/../../../.." && pwd)"
cd "$ROOT" || exit 0

if [ ! -d ".git" ]; then
  echo "❌ 不是 git 仓库"
  exit 0
fi

echo "===== 文件变更清单 (since=$SINCE, scope=$SCOPE) ====="
echo "格式: <状态> <文件路径>  (A=新增, M=修改, D=删除, R=重命名)"
echo ""

git log --since="$SINCE" --no-merges --name-status --pretty=format:"" -- "$SCOPE" \
  | grep -E "^[AMDR]" \
  | sort -u

echo ""
echo "===== 按模块聚合 ====="
git log --since="$SINCE" --no-merges --name-status --pretty=format:"" -- "$SCOPE" \
  | grep -E "^[AMDR]" \
  | awk '{print $2}' \
  | awk -F'/' '{
      if ($0 ~ /^workspace\/src\/main\/java\//) {
        for (i=1; i<=NF; i++) {
          if ($i == "controller" || $i == "service" || $i == "domain" || $i == "dao" || $i == "repository" || $i == "infra" || $i == "config") { print $i; next }
        }
        print "main-java"
      }
      else if ($0 ~ /^workspace\/src\/main\/resources\//) print "configuration"
      else if ($0 ~ /^workspace\/src\/test\//) print "tests"
      else if ($0 ~ /^workspace\//) print "backend-project"
      else if ($0 ~ /^docs\/contracts\//) print "contracts"
      else if ($0 ~ /^docs\//) print "workflow-docs"
      else if ($0 ~ /^\.claude\// || $0 ~ /^tools\//) print "workflow"
      else print "root"
    }' \
  | sort | uniq -c | sort -rn

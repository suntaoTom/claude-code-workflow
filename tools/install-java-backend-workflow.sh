#!/usr/bin/env bash
# install-java-backend-workflow.sh — 安全安装母版到目标仓库；默认不覆盖现有文件。
set -eu

SOURCE_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TARGET=""
DRY_RUN=0
WITH_CI=0

usage() {
  printf '%s\n' '用法: install-java-backend-workflow.sh <target-root> [--dry-run] [--with-ci]'
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --dry-run) DRY_RUN=1; shift ;;
    --with-ci) WITH_CI=1; shift ;;
    -h|--help) usage; exit 0 ;;
    -*) echo "❌ 未知参数：$1" >&2; usage; exit 2 ;;
    *)
      if [ -n "$TARGET" ]; then echo "❌ 只能指定一个目标目录" >&2; exit 2; fi
      TARGET="$1"
      shift
      ;;
  esac
done

if [ -z "$TARGET" ]; then usage; exit 2; fi
TARGET="$(cd "$TARGET" 2>/dev/null && pwd || true)"
if [ -z "$TARGET" ] || [ "$TARGET" = "$SOURCE_ROOT" ]; then
  echo "❌ 目标目录必须存在且不能是母版自身" >&2
  exit 2
fi

copy_if_missing() {
  source_path="$1"
  target_path="$TARGET/$2"
  if [ -e "$target_path" ]; then
    printf 'SKIP existing %s\n' "$2"
    return 0
  fi
  printf 'ADD %s\n' "$2"
  if [ "$DRY_RUN" -eq 0 ]; then
    mkdir -p "$(dirname "$target_path")"
    cp "$source_path" "$target_path"
  fi
}

copy_tree_if_missing() {
  source_dir="$1"
  relative_dir="$2"
  while IFS= read -r -d '' source_path; do
    relative_path="${source_path#$SOURCE_ROOT/}"
    copy_if_missing "$source_path" "$relative_path"
  done < <(find "$source_dir" -type f -print0)
}

printf '%s\n' "安装母版：$SOURCE_ROOT → $TARGET"

copy_tree_if_missing "$SOURCE_ROOT/.claude" .claude
copy_if_missing "$SOURCE_ROOT/CLAUDE.md" CLAUDE.md
copy_if_missing "$SOURCE_ROOT/.workflow-manifest.yml" .workflow-manifest.yml
copy_if_missing "$SOURCE_ROOT/docs/backend-project-profile.yml" docs/backend-project-profile.yml
copy_if_missing "$SOURCE_ROOT/workspace/README.md" workspace/README.md
copy_if_missing "$SOURCE_ROOT/tools/README.md" tools/README.md
copy_if_missing "$SOURCE_ROOT/tools/backend.sh" tools/backend.sh
copy_if_missing "$SOURCE_ROOT/tools/gen_api_md.py" tools/gen_api_md.py
copy_if_missing "$SOURCE_ROOT/tools/validate-prd.py" tools/validate-prd.py
copy_if_missing "$SOURCE_ROOT/tools/validate-tasks.py" tools/validate-tasks.py
copy_if_missing "$SOURCE_ROOT/tools/check-traceability.py" tools/check-traceability.py
copy_tree_if_missing "$SOURCE_ROOT/tools/tests" tools/tests
copy_tree_if_missing "$SOURCE_ROOT/docs/contracts" docs/contracts
copy_tree_if_missing "$SOURCE_ROOT/docs/examples" docs/examples
copy_if_missing "$SOURCE_ROOT/docs/apis/README.md" docs/apis/README.md
copy_if_missing "$SOURCE_ROOT/docs/contracts/README.md" docs/contracts/README.md
copy_if_missing "$SOURCE_ROOT/docs/prds/_template.md" docs/prds/_template.md
copy_if_missing "$SOURCE_ROOT/docs/prds/REVIEW.md" docs/prds/REVIEW.md
copy_if_missing "$SOURCE_ROOT/docs/tasks/README.md" docs/tasks/README.md
copy_if_missing "$SOURCE_ROOT/docs/tasks/_template.json" docs/tasks/_template.json
copy_if_missing "$SOURCE_ROOT/docs/test-reports/_template.md" docs/test-reports/_template.md
copy_if_missing "$SOURCE_ROOT/docs/test-reports/README.md" docs/test-reports/README.md
copy_if_missing "$SOURCE_ROOT/docs/bug-reports/_template.md" docs/bug-reports/_template.md
copy_if_missing "$SOURCE_ROOT/docs/bug-reports/README.md" docs/bug-reports/README.md
copy_if_missing "$SOURCE_ROOT/docs/reports/security/README.md" docs/reports/security/README.md

if [ "$WITH_CI" -eq 1 ]; then
  copy_if_missing "$SOURCE_ROOT/templates/ci/ci-java.yml" .github/workflows/ci-java.yml
  copy_if_missing "$SOURCE_ROOT/templates/ci/gitlab-ci.yml" .gitlab-ci.yml
else
  printf '%s\n' 'SKIP CI/deploy templates (use --with-ci after reviewing platform ownership)'
fi

printf '%s\n' '完成：已有文件未覆盖；请填写 docs/backend-project-profile.yml，并确认 CLAUDE.md/CI 的项目特定内容。'

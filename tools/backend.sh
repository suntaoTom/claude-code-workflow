#!/usr/bin/env bash
# backend.sh — 从仓库根目录统一调用 workspace Maven 工程。
set -u

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PROJECT="$ROOT/workspace"
POM="$PROJECT/pom.xml"

usage() {
  printf '%s\n' '用法: ./tools/backend.sh <validate|spotless:check|test|verify|package|run> [--profile <profile>] [--dry-run] [Maven 参数...]'
}

command_name="${1:-}"
if [ -z "$command_name" ] || [ "$command_name" = "--help" ] || [ "$command_name" = "-h" ]; then
  usage
  [ -n "$command_name" ] && exit 0 || exit 2
fi
shift

profile=""
dry_run=0
maven_args=()
while [ "$#" -gt 0 ]; do
  case "$1" in
    --profile)
      if [ "$#" -lt 2 ]; then
        echo "❌ --profile 缺少值" >&2
        exit 2
      fi
      profile="$2"
      shift 2
      ;;
    --dry-run)
      dry_run=1
      shift
      ;;
    *)
      maven_args+=("$1")
      shift
      ;;
  esac
done

if [ ! -f "$POM" ] && [ "$dry_run" -eq 0 ]; then
  echo "ℹ️ workspace/pom.xml 不存在：后端项目尚未接入母版，跳过 Maven 操作" >&2
  exit 3
fi

case "$command_name" in
  validate|spotless:check|test|verify|package)
    goals=("$command_name")
    ;;
  run)
    goals=(spring-boot:run)
    ;;
  *)
    echo "❌ 不支持的 Maven 操作：$command_name" >&2
    usage
    exit 2
    ;;
esac

if [ -n "$profile" ]; then
  if [ "$command_name" = "run" ]; then
    goals+=("-Dspring-boot.run.profiles=$profile")
  else
    goals+=("-P$profile")
  fi
fi

if [ "$dry_run" -eq 1 ]; then
  printf 'mvn -f %q -B -ntp' "$POM"
  printf ' %q' "${goals[@]}"
  if [ "${#maven_args[@]}" -gt 0 ]; then
    printf ' %q' "${maven_args[@]}"
  fi
  printf '\n'
  exit 0
fi

if [ -x "$PROJECT/mvnw" ]; then
  exec "$PROJECT/mvnw" -f "$POM" -B -ntp "${goals[@]}" "${maven_args[@]}"
fi
exec mvn -f "$POM" -B -ntp "${goals[@]}" "${maven_args[@]}"

#!/usr/bin/env bash
# Visual QA — 截图 vs 设计稿像素对比（支持 Web / Android / 鸿蒙三端）
#
# 用法:
#   bash docs/designs/screenshots/run-visual-qa.sh <reference_image> [platform] [device_id]
#
# 参数:
#   reference_image  设计稿路径，如：
#                    docs/designs/screenshots/reference/主功能-首页/01_home.png
#   platform         web | android | ohos | auto（默认 auto）
#                    auto: 检测到 adb/hdc 设备 → mobile；否则 → web
#   device_id        多台设备时指定，如：
#                    Android: adb devices 输出的序列号，如 emulator-5554 / R3CR40XXXXX
#                    鸿蒙:    hdc list targets 输出，如 127.0.0.1:5555 / FMR0XXXXX
#
# 输出（镜像 reference 目录结构）:
#   actual/<分类>/<文件名>/actual.png        — 设备/浏览器截图
#   actual/<分类>/<文件名>/diff.png          — 差值图（红=差异区域）
#   actual/<分类>/<文件名>/side-by-side.png  — 左右对比图（蓝框=设计稿，绿框=实际）
#   actual/<分类>/<文件名>/qa-result.json    — 量化指标
#
# 示例:
#   reference/账号体系/01_welcome.jpg → actual/账号体系/01_welcome/actual.png ...
#   reference/主功能/01_home.png      → actual/主功能/01_home/actual.png ...

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../../.." && pwd)"
WORKSPACE_DIR="$ROOT_DIR/workspace"
REF_BASE_DIR="$SCRIPT_DIR/reference"

REFERENCE="${1:-}"
PLATFORM="${2:-auto}"
DEVICE_ID="${3:-}"   # 留空时自动取第一个设备

PORT=8000   # Web 模式 dev server 端口，按项目修改

# ── 颜色输出 ───────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; NC='\033[0m'; BOLD='\033[1m'

log()  { echo -e "${BLUE}[visual-qa]${NC} $*" >&2; }
ok()   { echo -e "${GREEN}✅${NC} $*" >&2; }
warn() { echo -e "${YELLOW}⚠️ ${NC} $*" >&2; }
fail() { echo -e "${RED}❌${NC} $*" >&2; }

# ── HDC PATH（鸿蒙工具链，macOS DevEco Studio 默认位置）─────────────────────────
export PATH="/Applications/DevEco-Studio.app/Contents/sdk/default/openharmony/toolchains:$PATH"

# ── 参数检查 ───────────────────────────────────────────────────────────────────
if [[ -z "$REFERENCE" ]]; then
  fail "用法: bash run-visual-qa.sh <reference_image> [web|android|ohos|auto] [device_id]"
  fail "示例: bash run-visual-qa.sh 'docs/designs/screenshots/reference/主功能/01_home.png' android"
  exit 1
fi

if [[ ! -f "$REFERENCE" ]]; then
  fail "设计稿文件不存在: $REFERENCE"
  exit 1
fi

# ── 计算输出目录（镜像 reference 结构）──────────────────────────────────────────
# reference/分类/01_name.png → actual/分类/01_name/
REF_ABS="$(cd "$(dirname "$REFERENCE")" && pwd)/$(basename "$REFERENCE")"
REF_STEM="${REF_ABS%.*}"
REL_STEM="${REF_STEM#$REF_BASE_DIR/}"
ACTUAL_DIR="$SCRIPT_DIR/actual/$REL_STEM"
mkdir -p "$ACTUAL_DIR"

ACTUAL="$ACTUAL_DIR/actual.png"
DIFF="$ACTUAL_DIR/diff.png"
SIDE="$ACTUAL_DIR/side-by-side.png"
RESULT="$ACTUAL_DIR/qa-result.json"

# ── 依赖检查 ───────────────────────────────────────────────────────────────────
check_deps() {
  if ! command -v magick &>/dev/null; then
    warn "ImageMagick 未安装，正在安装..."
    brew install imagemagick
  fi
}

# ── 平台自动检测 ───────────────────────────────────────────────────────────────
detect_platform() {
  local ohos_count=0 adb_count=0
  command -v hdc &>/dev/null && ohos_count=$(hdc list targets 2>/dev/null | grep -v "^$" | wc -l | tr -d ' ') || true
  command -v adb &>/dev/null && adb_count=$(adb devices 2>/dev/null | grep -v "List of" | grep -v "^$" | grep "device$" | wc -l | tr -d ' ') || true

  if [[ "$ohos_count" -gt 0 ]]; then echo "ohos"
  elif [[ "$adb_count" -gt 0 ]]; then echo "android"
  else echo "web"
  fi
}

# ── Web 截图（Playwright）──────────────────────────────────────────────────────
take_screenshot_web() {
  rm -f "$ACTUAL_DIR"/*.png "$ACTUAL_DIR"/*.json 2>/dev/null || true

  if ! command -v npx &>/dev/null; then
    fail "npx 未找到，请先安装 Node.js"
    exit 1
  fi

  local dev_pid="" dev_started=false

  lsof -ti tcp:$PORT | xargs kill -9 2>/dev/null || true

  log "启动 dev server（port $PORT）..."
  cd "$ROOT_DIR"
  pnpm dev &>/dev/null &
  dev_pid=$!
  dev_started=true

  log "等待 dev server 就绪（最多 30s）..."
  for i in $(seq 1 30); do
    curl -s "http://localhost:$PORT" &>/dev/null && break
    sleep 1
  done
  cd "$SCRIPT_DIR"

  log "Playwright 截图 http://localhost:$PORT ..."
  cd "$WORKSPACE_DIR"
  npx playwright screenshot \
    --browser chromium \
    --full-page \
    --viewport-size "1440,900" \
    --wait-for-timeout 2000 \
    "http://localhost:$PORT" \
    "$ACTUAL" >&2

  if [[ "$dev_started" == "true" && -n "$dev_pid" ]]; then
    kill "$dev_pid" 2>/dev/null || true
    log "已关闭 dev server"
  fi

  if [[ ! -f "$ACTUAL" ]] || [[ ! -s "$ACTUAL" ]]; then
    fail "截图失败，文件不存在或为空: $ACTUAL"
    exit 1
  fi
  ok "截图完成: $ACTUAL"
}

# ── Android 截图（adb）────────────────────────────────────────────────────────
take_screenshot_android() {
  rm -f "$ACTUAL_DIR"/*.png "$ACTUAL_DIR"/*.json 2>/dev/null || true

  local device
  if [[ -n "$DEVICE_ID" ]]; then
    device="$DEVICE_ID"
  else
    device=$(adb devices | grep "device$" | awk '{print $1}' | head -1)
  fi
  log "Android 设备: $device — 截图中..."
  adb -s "$device" exec-out screencap -p > "$ACTUAL"

  if [[ ! -f "$ACTUAL" ]] || [[ ! -s "$ACTUAL" ]]; then
    fail "截图失败，文件为空"
    exit 1
  fi
  ok "截图完成: $ACTUAL"
}

# ── 鸿蒙截图（hdc）————————————————————————————————————————————————————————————
# 注意：snapshot_display 只接受 .jpeg 扩展名，.png 会报错并生成空文件
take_screenshot_ohos() {
  rm -f "$ACTUAL_DIR"/*.png "$ACTUAL_DIR"/*.json 2>/dev/null || true

  local device remote="/data/local/tmp/qa_screen.jpeg"
  if [[ -n "$DEVICE_ID" ]]; then
    device="$DEVICE_ID"
  else
    device=$(hdc list targets 2>/dev/null | head -1 | tr -d '\r')
  fi
  log "鸿蒙设备: $device — 截图中..."
  hdc -t "$device" shell snapshot_display -f "$remote" >/dev/null 2>&1
  hdc -t "$device" file recv "$remote" /tmp/vqa-ohos-raw.jpeg >/dev/null 2>&1
  hdc -t "$device" shell rm "$remote" >/dev/null 2>&1
  magick /tmp/vqa-ohos-raw.jpeg "$ACTUAL" 2>/dev/null
  rm -f /tmp/vqa-ohos-raw.jpeg

  if [[ ! -f "$ACTUAL" ]] || [[ ! -s "$ACTUAL" ]]; then
    fail "截图失败，文件为空"
    exit 1
  fi
  ok "截图完成: $ACTUAL"
}

# ── 图像对比 ───────────────────────────────────────────────────────────────────
compare_images() {
  local ref_w ref_h
  ref_w=$(magick identify -format "%w" "$REFERENCE")
  ref_h=$(magick identify -format "%h" "$REFERENCE")
  log "设计稿尺寸: ${ref_w}×${ref_h}，缩放截图匹配..."

  magick "$ACTUAL" -resize "${ref_w}x${ref_h}!" /tmp/vqa-actual-resized.png 2>/dev/null

  local raw rmse_norm
  raw=$(magick compare -metric RMSE \
    -highlight-color "#FF3B30" \
    -lowlight-color  "#F0F0F0" \
    "$REFERENCE" /tmp/vqa-actual-resized.png "$DIFF" 2>&1 || true)
  rmse_norm=$(echo "$raw" | grep -oE '\([0-9.]+\)' | tr -d '()' | head -1 || echo "1.0")
  [[ -z "$rmse_norm" ]] && rmse_norm="1.0"

  # 左右对比图（蓝框=设计稿 / 绿框=实际截图）
  magick +append \
    \( "$REFERENCE"               -bordercolor "#0052FF" -border 4 \) \
    \( /tmp/vqa-actual-resized.png -bordercolor "#00AA44" -border 4 \) \
    "$SIDE" 2>/dev/null

  rm -f /tmp/vqa-actual-resized.png
  echo "$rmse_norm"
}

# ── P0/P1/P2 阈值（移动端）────────────────────────────────────────────────────
# Web 端项目可按需调整：P0<0.35 / P1<0.25 / P2<0.15
P0_THRESHOLD="0.20"
P1_THRESHOLD="0.10"
P2_THRESHOLD="0.05"

# ── 写 JSON 报告 ───────────────────────────────────────────────────────────────
write_json() {
  local rmse="$1" p0="$2" p1="$3" p2="$4"
  local similarity
  similarity=$(echo "$rmse" | awk '{printf "%.1f", (1 - $1) * 100}')

  cat > "$RESULT" <<JSON
{
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "platform": "$PLATFORM",
  "deviceId": "${DEVICE_ID:-auto}",
  "reference": "$REFERENCE",
  "actual": "$ACTUAL",
  "diff": "$DIFF",
  "sideBySide": "$SIDE",
  "metrics": {
    "rmseNormalized": $rmse,
    "similarityScore": $similarity
  },
  "grades": {
    "P0_structure": { "pass": $p0, "threshold": $P0_THRESHOLD, "label": "结构布局（必须通过）" },
    "P1_visual":    { "pass": $p1, "threshold": $P1_THRESHOLD, "label": "视觉 Token 整体（≥90% 相似）" },
    "P2_pixel":     { "pass": $p2, "threshold": $P2_THRESHOLD, "label": "像素级精确（≥95% 相似，不阻塞）" }
  }
}
JSON
}

# ── 打印报告 ───────────────────────────────────────────────────────────────────
print_report() {
  local rmse="$1" p0="$2" p1="$3" p2="$4"
  local similarity dev_label="${DEVICE_ID:-auto}"
  similarity=$(echo "$rmse" | awk '{printf "%.1f", (1 - $1) * 100}')

  echo ""
  echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "${BOLD}  📸 Visual QA 报告  [$PLATFORM · $dev_label]${NC}"
  echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo    "  参考: $REFERENCE"
  echo    "  实际: $ACTUAL"
  echo    ""
  echo -e "  $( [[ "$p0" == "true" ]] && echo "✅" || echo "❌" ) P0 结构布局     RMSE=$rmse  阈值<$P0_THRESHOLD  $( [[ "$p0" == "true" ]] && echo "通过" || echo "❌ 必须修复" )"
  echo -e "  $( [[ "$p1" == "true" ]] && echo "✅" || echo "⚠️ " ) P1 视觉 Token   RMSE=$rmse  阈值<$P1_THRESHOLD  $( [[ "$p1" == "true" ]] && echo "通过" || echo "⚠️  建议修复" )"
  echo -e "  $( [[ "$p2" == "true" ]] && echo "✅" || echo "📌" ) P2 像素精确     RMSE=$rmse  阈值<$P2_THRESHOLD  $( [[ "$p2" == "true" ]] && echo "通过" || echo "📌 记录，不阻塞" )"
  echo    ""
  echo    "  相似度: ${similarity}%"
  echo    ""
  echo    "  产出文件:"
  echo    "    差值图:  $DIFF"
  echo    "    对比图:  $SIDE"
  echo    "    JSON:   $RESULT"
  echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

  if [[ "$p0" == "false" ]]; then
    fail "P0 未通过，必须修复后重跑 /visual-qa"
    echo ""
  elif [[ "$p1" == "false" ]]; then
    warn "P1 有差异，建议用 /code 修复后重跑"
    echo ""
  else
    ok "视觉对比通过！"
    echo ""
  fi
}

# ── 主流程 ─────────────────────────────────────────────────────────────────────
main() {
  check_deps

  # 平台自动检测
  if [[ "$PLATFORM" == "auto" ]]; then
    PLATFORM=$(detect_platform)
    log "自动检测平台: $PLATFORM"
  fi

  # 截图
  log "开始 Visual QA — 平台: $PLATFORM，输出: $ACTUAL_DIR"
  case "$PLATFORM" in
    web)     take_screenshot_web ;;
    android) take_screenshot_android ;;
    ohos)    take_screenshot_ohos ;;
    *)
      fail "未知平台: $PLATFORM（支持 web / android / ohos / auto）"
      exit 1
      ;;
  esac

  # 对比
  RMSE=$(compare_images)

  P0=$(echo "$RMSE" | awk -v t="$P0_THRESHOLD" '{print ($1 < t) ? "true" : "false"}')
  P1=$(echo "$RMSE" | awk -v t="$P1_THRESHOLD" '{print ($1 < t) ? "true" : "false"}')
  P2=$(echo "$RMSE" | awk -v t="$P2_THRESHOLD" '{print ($1 < t) ? "true" : "false"}')

  write_json "$RMSE" "$P0" "$P1" "$P2"
  print_report "$RMSE" "$P0" "$P1" "$P2"

  [[ "$P0" == "false" ]] && exit 2
  exit 0
}

main "$@"

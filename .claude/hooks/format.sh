#!/bin/bash
# 前端自动格式化: 编辑 .ts/.tsx/.js/.jsx 文件后跑 prettier --write, 保持风格统一
# 触发时机: PostToolUse (Edit|Write)
# 设计: 只格式化、不做 lint/类型检查 (那些慢, 留给 /review / security-gate / commit 时机)
#   prettier 随 workspace 的 @umijs/lint 安装。

filepath="$CLAUDE_FILE_PATH"

# 非前端源码 / 路径为空 / 文件不存在 → 跳过
[ -z "$filepath" ] && exit 0
echo "$filepath" | grep -qE '\.(tsx?|jsx?)$' || exit 0
[ -f "$filepath" ] || exit 0

# 跳过 Umi 生成产物 (src/.umi) 与 *.d.ts 声明文件 (非手写源码)
echo "$filepath" | grep -qE '/\.umi/|\.d\.ts$' && exit 0

# 用 workspace 的 prettier 静默格式化; 失败 (prettier 缺 / 语法错) 不阻塞编辑
pnpm -C workspace exec prettier --write "$filepath" >/dev/null 2>&1 \
  || (cd workspace 2>/dev/null && npx --no-install prettier --write "$filepath" >/dev/null 2>&1) \
  || true
exit 0

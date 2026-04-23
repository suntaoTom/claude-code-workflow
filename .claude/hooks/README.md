# hooks/ — Claude Code Automation Hooks

> Configured in `.claude/settings.json`, executed automatically on specific events. Warn only — never block.

## File Manifest

| File | Trigger | Purpose |
|------|---------|---------|
| check-hardcode.sh | After each ts/tsx file edit/create | Scans for hardcoded Chinese strings; warns immediately on P0 rule violations |
| check-tasks-status.sh | At the start of each new session | Lists in-progress tasks; reminds where the last session left off |
| pre-commit-check.sh | Before git commit | Checks whether task status was forgotten to be updated to done |

## Adding a New Hook

1. Create a `.sh` script in this directory and run `chmod +x`
2. Add a comment at the top of the script stating: trigger event + purpose
3. Reference it under the corresponding event in `.claude/settings.json`: `".claude/hooks/xxx.sh"`
4. Update the file manifest in this README

## Available Environment Variables

| Variable | Available In | Description |
|----------|-------------|-------------|
| `$CLAUDE_FILE_PATH` | PostToolUse (Edit/Write) | Path of the file just edited |
| `$CLAUDE_TOOL_INPUT` | PreToolUse | Input content of the tool about to be executed |

## Design Principles

- Warn only, never block (exit 0, not exit 1)
- Silent when no issues; output only when something is wrong
- 5-second timeout; no heavy operations

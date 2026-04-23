# .claude/ — AI Automation Configuration

> The central Claude Code configuration hub for this project. Subdirectories are organized by responsibility, each with its own README.

## Directory Overview

| Directory/File | Responsibility | How It's Triggered |
|----------------|----------------|--------------------|
| [commands/](commands/) | Main workflow commands (eight-step process) | User explicitly types `/<name>` |
| [skills/](skills/) | Extended skill packs (ext-\*), includes scripts and reference materials | Explicit `/ext-xxx` or auto-invoked by AI based on description |
| [agents/](agents/) | Sub-agent definitions, supports parallel / isolated-context work | Spawned by the `Agent` tool inside main commands |
| [hooks/](hooks/) | Automated hook scripts, event-triggered | Events configured in `settings.json` (PostToolUse, etc.) |
| [rules/](rules/) | Long-lived, stable coding conventions for AI to read | Referenced on demand from `CLAUDE.md` |
| [settings.json](settings.json) | Shared hooks config (committed to git) | Loaded at Claude Code startup |
| settings.local.json | Personal permissions/env vars (gitignored) | Local only; does not affect the team |

## Quick Reference

### I want to...

| Scenario | Where to go |
|----------|-------------|
| See what slash commands are available | [commands/](commands/) |
| Add a new audit/analysis skill | Follow conventions in [skills/README.md](skills/README.md) |
| Trigger automated checks on certain events | See [hooks/README.md](hooks/README.md) for how to add hooks |
| Make the AI follow a coding rule | Add an `.md` file to [rules/](rules/) and reference it from `CLAUDE.md` |
| Run a large task in parallel | See [agents/README.md](agents/README.md) for how sub-agents work |
| Configure permissions to reduce confirmation prompts | Edit `settings.local.json` (not committed to git) |
| Configure a hook shared across the whole team | Edit `settings.json` (committed to git) |

## Commands / Skills / Agents / Hooks / Rules — Boundaries

| Mechanism | What it is | Best for | Characteristics |
|-----------|-----------|---------|-----------------|
| **Commands** (commands/) | Single `.md` file prompt template | Main eight-step workflow; pure reasoning workflows | User-triggered; runs in main context |
| **Skills** (skills/) | Folder + SKILL.md + scripts + assets | Tool-like tasks that need to run real commands and collect data | Explicit or auto-triggered; progressively loaded |
| **Agents** (agents/) | Sub-agent definition + isolated context | Parallel work / heavy tasks that protect the main context | Spawned by main command; isolated context |
| **Hooks** (hooks/) | Event-triggered scripts | Silent automated checks (non-blocking) | Runs in background; no AI decision required |
| **Rules** (rules/) | Long-lived, stable convention docs | Coding style / no-hardcode constraints, etc. | Referenced by `CLAUDE.md`; AI follows automatically |

## When Adding Something New

1. **Identify the type first** — use the boundary table above to find the right place; don't put it in the wrong spot
2. **Write a README or comments** — every subdirectory must be self-explanatory
3. **Update CLAUDE.md** — if it's a rule or new mechanism, the top-level `CLAUDE.md` must reference it
4. **Update WORKFLOW.md** — if users will interact with it, register it in the workflow manual

## Current Project Status

**Commands** (14): `/prd` `/prd-check` `/plan` `/plan-check` `/code` `/test` `/review` `/bug-check` `/fix` `/build` `/deploy` `/release` `/start` `/meta-audit`

**Skills** (4): `ext-dep-audit` `ext-perf-audit` `ext-a11y-check` `ext-changelog`

**Agents** (4): `test-writer` `code-reviewer` `bug-fixer` `meta-auditor` — see [agents/README.md](agents/README.md)

**Hooks** (3): `check-hardcode` `check-tasks-status` `pre-commit-check` — see [hooks/README.md](hooks/README.md)

**Rules** (5): `coding-style` `file-docs` `no-hardcode` `tech-stack` `testing`

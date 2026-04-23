# agents/ — Sub-Agent Definitions

> Specialized agents spawned by main commands via the `Agent` tool, each running in an **independent context**, supporting parallelism without polluting the main session.

## File Manifest

| Agent | Responsibility | Spawned By |
|-------|---------------|-----------|
| [test-writer.md](test-writer.md) | Generate tests for specified source files (reads `@rules` → writes `it()` per rule) | After `/code` completes / `/test` for multi-module parallelism |
| [code-reviewer.md](code-reviewer.md) | Read-only review of a file/directory, outputs issue list | `/review` splitting large directories / pre-PR self-check |
| [bug-fixer.md](bug-fixer.md) | Fix a single bug (from bug-report) | `/fix` for parallel handling of multiple bug reports |
| [meta-auditor.md](meta-auditor.md) | **God-mode** meta-audit, scans the entire codebase for inconsistencies/drift/dead links, outputs report to `docs/retrospectives/` | Triggered by `/meta-audit` command |

## Sub-Agents vs. Slash Commands

| | Slash Commands (commands/) | Sub-Agents (agents/) |
|---|---|---|
| Runs in | **Main context** | **Independent context** (created at spawn time) |
| Parallel | No, serial execution | Yes, multiple agents can run concurrently |
| Memory | Full main session visible | Only sees the passed-in prompt |
| Output | Written directly to main session | Returns a summary to main agent |
| Best for | User-triggered workflows | Independent sub-tasks spawned inside main commands |

**Why sub-agents**:

1. **Parallel acceleration** — 5 independent bugs reported in tests → spawn 5 `bug-fixer` agents in parallel, 5× faster than serial
2. **Protect main context** — reviewing a large directory reads many files; stuffing that into main context quickly overflows; let sub-agents run and return summaries
3. **Responsibility isolation** — sub-agents only see **the passed-in prompt**, free from main session pollution, producing more focused output

## Agent MD File Format

```markdown
---
name: <agent-name>                    # Unique identifier, matches filename
description: <one sentence> — when to spawn    # Main agent uses this to decide whether to use it
tools: [Read, Edit, Write, Bash, Grep, Glob]  # Optional, inherits by default
---

# <agent-name>

<Complete system prompt: role / input / execution steps / output format / boundaries>
```

### Key Fields

| Field | Description |
|-------|-------------|
| `name` | Main agent uses `subagent_type: "test-writer"` when calling the Agent tool |
| `description` | Critical to whether the main agent selects this agent — must include trigger scenario keywords |
| `tools` | Limits available tools. Read-only agents (like reviewer) should exclude Edit/Write |
| body | Complete prompt that becomes the sub-agent's system prompt |

## When to Write a New Agent

✅ **Suitable scenarios**:
- Parallelizable independent sub-tasks (fixing multiple bugs in parallel)
- Heavy read-only tasks that would bloat main context (large directory scanning)
- Independent second-opinion reviews (main agent wrote the code; let reviewer see it independently)
- Same type of task reused across multiple main commands (test-writer is used by both /code and /test)

❌ **Not suitable scenarios**:
- Complete user-triggered workflows → use commands/
- Need to run scripts for deterministic data → use skills/ package form
- Event-triggered automatic checks → use hooks/
- Simple one-off tasks → main agent handles directly; don't over-engineer

## Agent Writing Principles

- **Prompts must be self-contained** — sub-agents can't see main session history; input must be complete
- **Output must be structured** — sub-agent return is a message; consistent format makes it parseable by main agent
- **Minimize tool permissions** — reviewer shouldn't have Edit permission; test-writer shouldn't have delete permission
- **Avoid deep nesting** — sub-agents should not spawn further sub-agents in principle; keep it simple

# skills/ — Claude Code Skill Packages

> Extension skills in package form. Each package contains a `SKILL.md` main description + `scripts/` for deterministic scripts + `references/` for reference material.
> Difference from `commands/*.md` (single-file prompts): package form can run scripts to fetch real data, reducing AI guesswork.

## File Manifest

| Skill | Purpose | Trigger Scenario |
|-------|---------|-----------------|
| [prd-import/](prd-import/) | Convert non-Markdown requirement formats (.docx/.xlsx/.pptx → md) | Product hands over a Word/Excel/PPT spec, as the entry point for `/prd` |
| [ext-dep-audit/](ext-dep-audit/) | Dependency security and health audit | Dependency inspection / security scanning |
| [ext-perf-audit/](ext-perf-audit/) | Frontend performance audit | Page lag analysis / pre-release optimization |
| [ext-a11y-check/](ext-a11y-check/) | Accessibility WCAG 2.1 AA compliance check | Compliance audit / keyboard navigation support |
| [ext-changelog/](ext-changelog/) | Module-aggregated change impact report | Weekly reports / handoffs / retrospectives |

## Naming Conventions

- `ext-*` prefix = **optional extension skill**, used on demand, not part of the main flow
- No prefix = **main-flow companion skill**, supports a specific step in the Eight-Step process (e.g. `prd-import` supports the `/prd` entry point)

## Directory Structure Convention

```
skills/<skill-name>/
├── SKILL.md              # Main description, with frontmatter (name + description)
├── scripts/              # Deterministic scripts (optional)
│   └── xxx.sh            # Bash scripts that run real commands to collect data
└── references/           # Reference material (optional)
    └── xxx.md            # Large reference docs, loaded on demand (to avoid bloating context every time)
```

## SKILL.md Format

```markdown
---
name: <skill-name>           # Unique identifier, must match the directory name
description: <one sentence>  # Key: determines when AI auto-triggers this skill — be specific
---

# <skill-name>

<Full skill description: responsibilities / execution flow / output format / design principles>
```

### How to Write the `description` Field

This is the **sole basis** for whether AI automatically invokes a skill. It must include:
- **What it does** (one sentence)
- **When to use it** (specific keywords: "trigger when the user explicitly requests 'X / Y / Z'")

**Bad example** (too vague): `description: performance-related`
**Good example**: `description: Frontend performance audit. Analyzes bundle size, React render performance, network waterfall, memory leaks, and initial load. Trigger when the user explicitly requests "performance audit / page lag analysis / bundle size optimization / initial load optimization".`

## Script Conventions

- Placed in the `scripts/` subdirectory, named in kebab-case
- Top-of-file comment documents usage and parameters
- Unified path resolution: `ROOT="$(cd "$(dirname "$0")/../../../.." && pwd)"` to return to the repo root
- Do not `exit 1` on failure; output a message the AI can understand (scripts are a data source for AI, not a CI gate)
- Add execute permission: `chmod +x`

## References Conventions

- Placed in the `references/` subdirectory; all files are Markdown
- **Do not embed in SKILL.md** — reference on demand (use `[link](references/xxx.md)` in SKILL.md)
- Suitable content: WCAG rule lists, checklists, comparison tables, common anti-patterns
- Unsuitable content: changing business rules (those belong in the PRD)

## Adding a New Skill

1. Create the `skills/<new-skill-name>/` directory
2. Write `SKILL.md` (frontmatter + body)
3. Add `scripts/` and `references/` as needed
4. Add execute permission to scripts
5. Add a row to the File Manifest in this README
6. If it has an `ext-` prefix, register it in the "Extension Commands" section of `docs/WORKFLOW.md`

## skills/ vs commands/ — How to Choose

| Scenario | Where to Put It |
|----------|----------------|
| Pure prompt workflow with no scripts to run (e.g. `/prd` `/plan` `/code`) | `commands/*.md` |
| Needs to run scripts to fetch real data (bundle size / git log / pnpm output) | `skills/<name>/` package form |
| Has large reference material not suitable for injecting into context every time | `skills/<name>/references/` |
| Cross-project reuse (general-purpose capability) | Can be moved to `~/.claude/skills/` globally |

## Design Principles

- **Scripts fetch data; AI interprets** — if something can be measured deterministically, don't ask AI to estimate it
- **Progressive loading** — large reference docs go in `references/`; `SKILL.md` references them, doesn't embed them
- **Be specific in `description`** — include trigger keywords so AI can correctly identify when to invoke
- **Read-only by default** — analysis skills do not modify code directly; fixes go through `/fix`

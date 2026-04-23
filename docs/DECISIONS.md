# Architecture Decision Records (ADR)

> Records major framework design decisions, rationale, and alternatives considered. Future AI models and new team members can read this to understand "why things are the way they are," avoiding repeated mistakes or uninformed reversals.

## When to Add an Entry

| Should Record ✅ | No Need to Record ❌ |
|-----------------|----------------------|
| Introducing a new mechanism (command / skill / agent / hook / rule category) | Bug fixes / wording changes / file renames |
| Changing the form of an existing mechanism (e.g. `.md` → skill package) | Routine code changes (commit message is sufficient) |
| Constraining design choices (read-only / one-way dependency / hard gates) | Unvalidated ideas (open an issue first) |
| Decisions that were revisited (must document why it was revisited) | |

## Template

```markdown
## YYYY-MM-DD: One-line title

**Background**: The problem that triggered this decision
**Decision**: What was done, down to the specific files
**Rationale**: Why this option was chosen
**Alternatives**: Options considered but rejected + reasons for rejection
**Impact**: Related files/directories
```

## Rules

- Ordered reverse-chronologically; newest entry at the top
- Once written, do not edit old entries (decisions are historical facts; changes require a new entry noting "supersedes the XXX decision from YYYY-MM-DD")
- Keep each entry under 15 lines; link to details elsewhere

---

## 2026-04-20: Online documents (Feishu/Notion/Yuque etc.) will not have API integrations — use the "export + prd-import" path instead

**Background**: After `prd-import` gained support for local `.docx/.xlsx/.pptx`, the next question was online documents. Teams commonly write requirements in Feishu / Notion / Yuque / Tencent Docs / Google Docs, and what product managers hand over is often an online link rather than a file. "Can `/prd` read online links directly?" was a natural ask.

**Decision**: **No API integrations will be built for any platform.** The official paths are:
1. **Path A (recommended, available immediately)**: Users export from the platform as `.md` (Notion / Yuque) or `.docx` (Feishu / Tencent / Google / Confluence / DingTalk / Shimo), then process with the existing `prd-import` flow.
2. **Path B (advanced, user-configured)**: Recommended MCP servers (Notion / Google Drive have mature ones); the project **does not bundle any config** — users add them to `~/.claude/mcp.json` themselves.

Detailed export instructions for each platform are written into [.claude/skills/prd-import/references/formats.md](../.claude/skills/prd-import/references/formats.md#在线文档怎么办).

**Rationale**:
- **Maintenance cost is unsustainable** — Feishu / Notion / Yuque / Google all use completely different auth mechanisms (tenant_access_token / integration token / user token / OAuth); token refresh, permission scopes, rate limits, and SDK versioning are all moving targets. Supporting all of them would turn the framework from a "tool" into an "operations project."
- **ROI is too low** — 90% of teams use only 1–2 platforms; building all is wasteful. Supporting just one platform invites complaints about "why not X."
- **Path A is already good enough** — Every platform has an export feature; the manual cost is ~3 minutes, covers 100% of platforms, and once learned applies forever.
- **Fragility** — Platform UI changes, API deprecations, and token policy shifts can all break an integration silently; maintenance debt accumulates continuously.
- **Security** — Integrations require storing tokens; token leaks expose the entire account. No integration means no such risk.
- **MCP already solves this** — Community and official Anthropic MCP servers are a "user-side" decision, not a "project-side" decision; the project only needs to recommend, not maintain.

**Alternatives (rejected)**:
- **Build our own Feishu integration** — Even for Feishu alone (high-frequency for domestic teams), it requires managing tenant_access_token refresh + doc token permissions + a rich-text-block-to-markdown conversion layer; estimated 500+ lines of code + long-term maintenance, and only solves one platform.
- **URL scraping (public links)** — Only works for publicly shared documents; most team-internal docs are private. HTML parsing is fragile; cost/benefit ratio is terrible.
- **Build a unified "online document adapter" abstraction** — Looks elegant, but data models differ significantly across platforms; the resulting interface is either too tight (losing platform-specific features) or too loose (effectively no abstraction). A classic premature-abstraction trap.

**Impact**:
- `.claude/skills/prd-import/SKILL.md` — Add an "online documents" row to the input type table, pointing to the reference doc
- `.claude/skills/prd-import/references/formats.md` — Add an "What to do with online documents" section (including an export-path table for 9 major platforms + MCP guide + rationale for rejecting API integrations)
- `docs/WORKFLOW.md` — Add one row each to the Step 1 input type table and the quick-reference table

**Note**: If a team is heavily concentrated on a single platform and manual export is genuinely costly, **only then** consider a lightweight read-only integration for that one platform — but still evaluate whether an MCP server is a better alternative. Do not build integrations "for completeness."

---

## 2026-04-20: Non-Markdown requirements format entry extracted into the prd-import skill

**Background**: The `/prd` command only accepts text / Markdown / PDF / images (natively supported by Claude Code), but product managers and backend teams regularly hand over `.docx / .xlsx / .pptx` files — binary zip+XML that Claude cannot read directly. Users either paste manually (impractical for long documents) or save as PDF (losing formatting). The entire `/prd` main-flow entry was blocked.

**Decision**: Add a `.claude/skills/prd-import/` skill package + `workspace/scripts/prd-import.mjs` script to handle Word/Excel/PPT → Markdown conversion. The output is written to `docs/prds/_imports/<basename>-<date>.md`, then `/prd @<output>` runs the normal clarification flow. `/prd` itself is unchanged.

**Rationale**:
- **Clean separation of concerns** — Format conversion is a deterministic scripting task (defined input, standard output); it belongs in `skills/`. `/prd` is pure reasoning; it stays in `commands/`.
- **Traceable artifacts** — Converted output is preserved in `_imports/`; when reviewing the PRD, the source can be compared side by side — no opaque black box.
- **Minimal dependencies** — Uses `mammoth` (docx) + `xlsx` (excel), two npm packages installed inside `workspace/` reusing existing node_modules. PPTX uses native Node unzip + regex; no additional dependencies.
- **No breaking changes** — The `/prd` interface is unchanged; this is just a new pre-processing path. Users providing Markdown / plain text / PDF / images pay zero extra cost.

**Alternatives (rejected)**:
- **Extend `/prd` to auto-detect and convert** — Embedding the script call in the `/prd` prompt gives the smoothest UX, but violates the skill/command boundary (commands are pure prompts and should not depend on external scripts).
- **Rely on system-installed pandoc** — Not universally available; a hard dependency adds friction for first-time users. npm packages installed in workspace are set up automatically by `pnpm install`.
- **Ask users to paste manually or save as PDF** — Workable but poor UX; complex tables and long documents lose content.

**Naming choice**: No `ext-` prefix. The `ext-*` semantic is "optional extension" (performance audit / a11y, etc. — development works fine without them). `prd-import` is a **necessary complement to the main-flow entry point** (without it, doc-format requirements can't enter `/prd`), so it is classified as "no prefix = main-flow companion skill."

**Impact**:
- New: `.claude/skills/prd-import/{SKILL.md, references/formats.md}`, `workspace/scripts/prd-import.mjs`, `docs/prds/_imports/{.gitkeep, README.md}`
- Modified: `workspace/package.json` (+mammoth, +xlsx, +prd:import script), root `package.json` (+prd:import proxy), `.claude/skills/README.md` (register + add naming convention table), `docs/WORKFLOW.md` (Step 1 adds non-Markdown branch; quick-reference table adds one row)

---

## 2026-04-20: Test file location unified under workspace/tests/ (supersedes "co-located with source files")

**Background**: `.claude/rules/testing.md` and `.claude/agents/test-writer.md` originally specified "co-located with source files," but `.claude/commands/test.md` and existing code (`workspace/tests/features/list/`) already used the `workspace/tests/` mirroring `src/` structure. The 2026-04-20 meta-audit report (Top 3 Must-Fix) caught this conflict — rules diverging from code would cause `test-writer` to create a second inconsistent layout when generating new tests.

**Decision**: Standardize on `workspace/tests/` mirroring `workspace/src/`. All unit/component test paths follow `workspace/tests/<src-mirror-path>/<name>.test.ts(x)`; E2E tests remain in `workspace/tests/e2e/`. Synchronized updates to:
- `.claude/rules/testing.md` (location section)
- `.claude/agents/test-writer.md` (Step 3 location-selection table)
- `.claude/agents/meta-auditor.md` (traceability chain dimension check paths)
- `.claude/agents/bug-fixer.md` (test backfill paths)
- `CLAUDE.md` (testing spec summary "location")
- `.claude/commands/test.md` **left unchanged** (it was correct from the start)

**Rationale**:
- **Consistent with current state** — `workspace/tests/features/list/` already follows this layout; rules follow code, not the other way around.
- **Clean `src/` directory** — `src/` contains only production code; bundling / tsc / coverage scanning / path filtering are all simpler.
- **Test imports use the `@/` alias** — Avoids `../../../` relative paths; renaming source files doesn't force test file changes.
- **Unified CI command** — A single `pnpm test workspace/tests/` runs everything; no need to concatenate scattered paths under `src/`.

**Alternatives (rejected)**:
- **Co-located with source files (old rule)** — Advantage: tests are immediately visible when editing source. Disadvantage: `src/` mixes production artifacts and tests; import paths become a tangle of relative paths; tsc/lint/build need extra filtering rules.
- **`__tests__/` subdirectory (Jest-style)** — Halfway: suffers from both problems.

**Supersedes**: This entry supersedes the "co-located tests" implicit rule introduced on 2026-04-20 (it was never formally recorded, but was scattered across `testing.md` / `test-writer.md` / `CLAUDE.md`).

**Impact**: The 5 `.claude/` files listed above + `CLAUDE.md`. The existing `workspace/tests/features/list/` location is **not migrated** — it was already correct.

---

## 2026-04-20: Introduced the meta-audit mechanism (meta-auditor + /meta-audit)

**Background**: As the framework grew, commands/skills/agents/rules increasingly cross-reference each other. Concerns arose about rule drift, dead references, and internal inconsistencies. Manual inspection is not feasible.

**Decision**: Add a read-only sub-agent `meta-auditor` that scans 6 dimensions (rule violations / documentation drift / internal consistency / traceability chains / dead links / orphaned assets), triggered manually via `/meta-audit`, with reports written to `docs/retrospectives/YYYY-MM-DD-meta-audit.md`.

**Rationale**:
- Read-only observer that does not auto-fix — avoids the "self-modification loop" and "infinite optimization" anti-patterns.
- Hard constraints enforced at the tool layer, not by prompt — the agent's `tools: [Read, Grep, Glob, Write]`; Write is limited to the report path only.
- Manually triggered, not scheduled — reports nobody reads are just noise.
- Reports are immutable — the next scan generates a new report; trends emerge naturally from comparison.

**Alternatives**: Auto-fixing agent (high anti-pattern risk) / integrated into `/review` (mixes responsibilities) — both rejected.

**Impact**: `.claude/agents/meta-auditor.md`, `.claude/commands/meta-audit.md`, `docs/retrospectives/`

---

## 2026-04-20: ext-* tools upgraded from slash commands to Skill packages

**Background**: The 4 extension tools (`ext-dep-audit` / `ext-perf-audit` / `ext-a11y-check` / `ext-changelog`) were originally `.md` commands, but these tasks involve deterministic steps (`pnpm audit` / `git log` / bundle size). Relying on pure prompts to have AI infer results is unreliable.

**Decision**: Migrated to `.claude/skills/ext-*/` package format: `SKILL.md` + `scripts/*.sh` + `references/*.md`. Removed the original `.claude/commands/ext-*.md` files.

**Rationale**:
- Scripts produce data → AI interprets; results are reproducible.
- Progressive loading — `SKILL.md` frontmatter is small; body loaded on demand.
- `description` enables automatic triggering; users don't need to remember command names.

**Alternatives**: Migrate main-flow commands (`/prd` `/plan` `/code` `/test`) to skill packages as well — rejected. Those are pure reasoning workflows with no scripts to extract; they are better suited to `commands/`.

**Impact**: `.claude/skills/ext-*/`, `.claude/skills/README.md`

---

## 2026-04-20: PRD completeness check extracted as a standalone command (/prd-check)

**Background**: `/plan` originally embedded the PRD completeness check (5 hard gates) as step zero. Users iterating on a PRD who wanted to self-check had to run the entire `/plan`, resulting in slow feedback.

**Decision**: Extract `.claude/commands/prd-check.md` as a standalone command; `/plan` step zero is updated to **call** `/prd-check`. Both share the same rule set from a single source of truth.

**Rationale**:
- Real-time feedback — self-check any time while editing a PRD.
- Single source of truth — check logic lives in one place; no risk of divergence.
- Catching issues at the entry point is cheaper than catching them downstream (tasks / code / tests).

**Impact**: `.claude/commands/prd-check.md`, `.claude/commands/plan.md`

---

## 2026-04-20: @rules designated as the sole source of test assertions

**Background**: Source file JSDoc originally only had `@prd`; during testing, AI inferred expectations by reading the source code. When the source had a bug, the tests were wrong too.

**Decision**: Source file JSDoc must include `@rules` (verbatim business rules; AI paraphrasing is not permitted). `/test` treats `@rules` as the **sole source** for assertions — one `it()` per rule.

**Rationale**:
- Requirements → code → tests are aligned to a single source of truth; AI inference is not given a foothold.
- When a business rule changes, `@rules` in the source is updated; tests automatically break → forced alignment.
- `@prd` points to the original document; `@rules` lives in the code — dual anchoring prevents broken chains.

**Alternatives**: `/test` reads the PRD directly — rejected; cross-file transformation introduces uncertainty.

**Impact**: `.claude/rules/file-docs.md`, `.claude/rules/testing.md`, `.claude/commands/code.md`, `.claude/commands/test.md`

---

## 2026-04-20: 4 sub-agents with defined roles (test-writer / code-reviewer / bug-fixer / meta-auditor)

**Background**: Reviewing large directories / fixing multiple bugs in parallel / running heavy read-only scans in the main context risks context overflow, or forfeits the benefit of parallelism.

**Decision**: Created `.claude/agents/` with 4 sub-agents, spawned by main commands via the `Agent` tool, each running in an independent context.

| Agent | Tool Permissions | Spawned By | Why |
|-------|-----------------|------------|-----|
| test-writer | R / W / E / Bash | `/code` after / `/test` | Tests can run in parallel |
| code-reviewer | R (read-only) | `/review` | Independent perspective + read-only prevents accidental edits |
| bug-fixer | R / W / E / Bash | `/fix` | Parallel bug fixing for speed |
| meta-auditor | R + W (report only) | `/meta-audit` | Heavy scan + read-only hard constraint |

**Rationale**: Minimum tool permissions — read-only agents don't have Edit; accidental modification is prevented at the technical layer. Independent contexts produce more focused output, uncontaminated by the main session.

**Impact**: `.claude/agents/*.md`, `.claude/agents/README.md`

---

## 2026-04-20: .claude/ mechanisms explicitly divided into 5 categories (commands / skills / agents / hooks / rules)

**Background**: Various `.md` files had ambiguous responsibilities. New team members didn't know where to put things, and couldn't tell how things were triggered.

**Decision**: 5 mechanism types + 5 directories + a `.claude/README.md` navigation entry point. Triggering methods, parallelism, and context isolation all differ — they cannot be used interchangeably.

| Mechanism | Best For | Trigger Method |
|-----------|---------|----------------|
| Commands (`commands/`) | Main workflows (pure reasoning) | User types `/<name>` |
| Skill packages (`skills/`) | Tasks that run scripts to collect data | Explicit or AI automatic |
| Agents (`agents/`) | Parallel work / protecting the main context | Main command spawns via Agent |
| Hooks (`hooks/`) | Silent automated checks | `settings.json` events |
| Rules (`rules/`) | Coding constraints | Referenced from `CLAUDE.md` |

**Impact**: `.claude/README.md`, each subdirectory `README.md`

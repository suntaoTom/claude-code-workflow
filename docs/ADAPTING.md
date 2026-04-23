# Cross-Discipline Adaptation Checklist

> This repository is currently an "AI-driven **frontend** engineering workflow framework." The vast majority of its mechanisms are domain-agnostic — swap out `rules/` and `workspace/` and it works for backend / data / mobile / DevOps / QA / design / product / writing / research, and any other discipline.
>
> This document outlines **what to keep as-is, what to replace, and what is optional**, along with a step-by-step migration checklist for adapting from the frontend template to another discipline.

---

## Three-Layer Structure

Break the framework into three layers to decide what can cross discipline boundaries:

| Layer | Contents | Cross-Discipline Reusability |
|-------|----------|------------------------------|
| **Core Layer** | Collaboration mechanisms + workflow skeleton + traceability + hard gates + design principles | ✅ Keep as-is, no changes needed |
| **Domain Layer** | Coding / testing / no-hardcode rules in `rules/` | ⚠️ Keep the structure, replace the content |
| **Discipline-Specific Layer** | `workspace/` workspace + domain assumptions in `commands/` | ❌ Replace entirely |

---

## Part 1: Keep As-Is (Domain-Agnostic Core)

The following requires no changes — take it and use it directly:

### 1.1 Collaboration Mechanisms (the `.claude/` Five-Pack)

| Mechanism | Purpose | Cross-Discipline Usage |
|-----------|---------|------------------------|
| `commands/*.md` | Prompts for fixed workflows | Replace content, keep structure; the Eight-Step names can stay |
| `skills/*/SKILL.md` | Reusable toolkits | Replace tools, keep structure |
| `agents/*.md` | Specialist sub-agents | Replace persona, keep framework |
| `hooks/*` | Lifecycle hooks | Keep as-is |
| `rules/*.md` | Hard rules | Keep structure, rewrite content |

### 1.2 Eight-Step Skeleton (command names can be reused verbatim)

```
/prd → /plan → /code → /test → /review → /build → /deploy → /release
  ↓       ↓       ↓       ↓        ↓         ↓        ↓         ↓
 Req   Break  Impl  Verify  Review  Artifact  Deliver  Release
```

**The abstract meaning of each step is cross-discipline** — only the "deliverable" changes (see the mapping table in Part 3).

Auxiliary commands are equally universal: `/prd-check` `/plan-check` `/bug-check` `/fix` `/start` `/meta-audit`.

### 1.3 Traceability Chain

```
Requirements anchor  →  Task ID  →  References in deliverables (@prd/@rules/@task)  →  Validation cases
```

This chain works for code, SQL, Terraform, Figma files, or research papers. The key is **every deliverable is annotated with its source**.

### 1.4 Hard Gate Pattern

`/prd-check` blocks before `/plan`; `/plan-check` blocks before `/code`.

**General principle**: Between any two phases there should be a `check` command to intercept "upstream unfilled placeholders" and "missing downstream contract dependencies." The specific checks change per discipline; the mechanism does not.

### 1.5 Design Principles (shared across all disciplines)

1. **Traceability**: Every deliverable can be traced back to a requirement
2. **Human review at critical nodes**: Requirements / breakdown / review / release must have human sign-off
3. **Failures are explicitly visible**: No silent degradation, no skipping, no silent fallbacks

### 1.6 Documentation Infrastructure

| File | Purpose | Cross-Discipline Usage |
|------|---------|------------------------|
| `docs/DECISIONS.md` | ADR | Records architecture/process decisions; not discipline-specific |
| `docs/retrospectives/` | meta-audit reports | Periodic self-checks; not discipline-specific |
| Directory-level `README.md` | File manifests | Every directory should have one |
| Deliverable header JSDoc / comment block | `@prd` `@task` `@rules` anchors | Syntax varies (Python uses docstrings, SQL uses block comments, Figma uses component descriptions), semantics are the same |

---

## Part 2: Keep Structure, Replace Content (Domain Layer)

Keep the filenames and outlines of the following files; rewrite the content for your discipline:

### 2.1 `.claude/rules/tech-stack.md`

**Replace**: Framework / libraries / toolchain

| Discipline | Replace With |
|------------|-------------|
| Frontend | UmiJS + React + antd (current) |
| Backend | Spring Boot / Express / Gin / FastAPI / Rails |
| Data Engineering | dbt / Airflow / Spark / Flink / Kafka |
| Mobile (iOS) | Swift + SwiftUI + Combine |
| Mobile (Android) | Kotlin + Jetpack Compose |
| Cross-platform | Flutter / React Native |
| DevOps/SRE | Terraform + Ansible + Helm + ArgoCD |
| QA | Playwright / Cypress / Selenium + Allure |
| Design | Figma + Design Token toolchain |
| Product | Notion / Feishu / Jira + data dashboards |
| Technical Writing | Markdown + MkDocs / Docusaurus + mermaid |
| Research | Python + Jupyter + LaTeX + Git LFS |

### 2.2 `.claude/rules/no-hardcode.md`

**Replace**: Specific scenarios defining "what counts as hardcoding"

| Discipline | What Must Not Be Hardcoded |
|------------|---------------------------|
| Frontend | Copy / colors / API URLs / enums / sizes / magic numbers |
| Backend | Config / secrets / DB connection strings / rate limits / timeouts / error codes |
| Data | Schema paths / table name prefixes / partition fields / retry thresholds |
| Mobile | Copy / theme colors / APIs / version numbers / feature flags |
| DevOps | Resource specs / domains / account IDs / regions / AMIs |
| QA | Accounts / environment URLs / wait times / assertion thresholds |
| Design | Color values (use tokens) / font sizes / border radii / spacing |
| Writing | Links / version numbers / product names (use variables/macros) |

**General principle**: Any value that "may change, differs across environments/tenants, or may be referenced in multiple places" must not be hardcoded. Config must be layered (global → module → instance) with no large-scale duplication.

### 2.3 `.claude/rules/coding-style.md` (or rename to `authoring-style.md`)

**Replace**: Naming conventions, file organization, and comment conventions for your discipline

- Code disciplines (frontend / backend / mobile / data / DevOps) → keep the "coding style" name
- Non-code disciplines → rename to the appropriate "authoring style":
  - Design: design-style.md (naming hierarchy / layer conventions / component reuse)
  - Product: prd-style.md (structured writing / user story format)
  - Writing: writing-style.md (tone / structure / citations)
  - Research: research-style.md (experiment logging / data management / reproducibility standards)

### 2.4 `.claude/rules/testing.md` (or rename to `validation.md`)

**Replace**: Validation methods for your discipline

| Discipline | Validation Method |
|------------|------------------|
| Frontend | Vitest + Playwright |
| Backend | JUnit / pytest / go test + integration tests + contract tests |
| Data | dbt test / great_expectations / data quality assertions |
| Mobile | XCTest / Espresso / Flutter test + device regression |
| DevOps | terratest / conftest / policy-as-code + game days |
| QA | Test reports + case coverage matrix |
| Design | Usability testing + a11y audit + design review checklist |
| Product | Acceptance cases + analytics event validation |
| Writing | Peer review + link/terminology consistency check |
| Research | Result reproduction + statistical significance testing |

**General principle**: The **sole source of validation assertions is the requirements rules (`@rules`)** — not AI inference from reading the deliverable. This holds regardless of discipline.

### 2.5 `.claude/rules/file-docs.md`

**Replace**: Syntax for attaching comments/metadata; preserve the semantics

| Discipline | How to Attach `@prd` `@task` `@rules` |
|------------|--------------------------------------|
| Frontend / Backend | File-header JSDoc / docstring |
| Data (SQL) | File-header block comment `/* @prd ... */` |
| Data (dbt) | Model `description` YAML field |
| Mobile (Swift) | `/// @prd ...` |
| DevOps (Terraform) | `# @prd ...` block + `description` parameter |
| Design (Figma) | Component description field + page-level description |
| Product (PRD) | The PRD itself; `@task` attached to user stories |
| Writing | Frontmatter `prd: xxx, task: xxx` |
| Research | Experiment script docstring + first Jupyter cell |

---

## Part 3: Eight-Step Discipline Mapping Table

The abstract semantics of each step are unchanged; only the deliverables change per discipline:

| Step | Abstract Meaning | Frontend | Backend | Data | Mobile | DevOps | QA | Design | Product | Research |
|------|-----------------|----------|---------|------|--------|--------|-----|--------|---------|---------|
| `/prd` | Solidify requirements | PRD | API requirements doc | Metric definitions | Feature spec | SLO/runbook requirements | Quality goals | Design brief | MRD/PRD | Research questions + hypotheses |
| `/plan` | Break into tasks | Component/hook/api list | Controller/service/model list | DAG + table schema | Screen/component list | IaC module breakdown | Test plan + case matrix | Information architecture + component list | Feature breakdown + priorities | Experiment design |
| `/code` | Implement | TypeScript code | Java/Go/Python code | SQL / dbt / Airflow DAG | Swift/Kotlin/Dart | Terraform/Helm | Automation scripts | Figma components | PRD body | Experiment scripts/analysis |
| `/test` | Validate | Vitest + Playwright | JUnit/pytest + integration | dbt test / GE | XCTest/Espresso | terratest/conftest | Execute + report | Usability testing | Acceptance cases | Result reproduction |
| `/review` | Review | Code review | Code review | SQL/DAG review | Code review | IaC review | Test report review | Design review | PRD review | Peer review |
| `/build` | Produce artifact | Static bundle | Docker image | Task image/jar | .ipa / .apk | Helm chart / plan output | Test case library | Design spec delivery package | Documentation package | Paper draft |
| `/deploy` | Deliver | CDN/OSS | K8s/Serverless | Scheduling platform registration | TestFlight/internal beta | Apply to target environment | Test environment deployment | Token release | Requirements registration | Submission |
| `/release` | Publish | Stable release + canary | Stable release + canary | Live metrics | App Store/Play Store | Change announcement + rollback plan | Quality sign-off | DS version number | Requirements announcement | Publication + review response |

---

## Part 4: Optional Modules (Pick and Choose by Discipline)

The following modules are not needed by all disciplines — delete them outright if unused:

| Module | Disciplines That Need It | Disciplines That Don't |
|--------|--------------------------|------------------------|
| OpenAPI type generation | Frontend/backend/mobile with contract integrations | Design/product/writing/research |
| i18n conventions | User-facing products (frontend/mobile/copy) | Backend/DevOps/data (generally not needed) |
| Design Token | Frontend/mobile/design | Backend/data/DevOps |
| Accessibility audit (`ext-a11y-check`) | Frontend/mobile/design | Others |
| Performance audit (`ext-perf-audit`) | Frontend/mobile/backend/data | Writing/product/design |
| Dependency audit (`ext-dep-audit`) | All disciplines with dependency management | — |

**Principle**: If unsure whether to keep something, leave it for now. If you're certain it's unused, delete the entire block (don't leave empty shells).

---

## Part 5: Migration Steps (Forking This Repo for a New Discipline)

```
1. Fork this repo and rename it
   └─ Suggested naming: ai-<discipline>-automation  (e.g. ai-backend-automation)

2. Keep unchanged
   ├─ .claude/commands/*.md            (Eight-Step skeleton; change content, not files)
   ├─ .claude/agents/*.md              (bug-fixer / code-reviewer / meta-auditor / test-writer etc.; change persona, not mechanism)
   ├─ .claude/hooks/*                  (lifecycle hooks; generally usable as-is)
   ├─ docs/WORKFLOW.md                 (update deliverable descriptions per step; keep the flow)
   ├─ docs/DECISIONS.md                (clear content; keep format)
   └─ docs/retrospectives/             (clear content)

3. Rewrite .claude/rules/*.md
   ├─ tech-stack.md          ← swap in your tech stack
   ├─ no-hardcode.md         ← swap in discipline-specific "no hardcoding" scenarios
   ├─ coding-style.md        ← replace with your discipline's authoring conventions (rename if needed)
   ├─ file-docs.md           ← replace with your discipline's metadata attachment method
   └─ testing.md             ← replace with your discipline's validation method (rename if needed)

4. Rewrite workspace/
   ├─ Frontend  → workspace/ is a UmiJS project
   ├─ Backend   → workspace/ is a Spring/Express/Gin project
   ├─ Data      → workspace/ is a dbt/Airflow project
   ├─ Design    → workspace/ is Figma files + design token source
   └─ Writing/Research → workspace/ is a Markdown/LaTeX file collection

5. Update CLAUDE.md (onboarding guide)
   ├─ P0 rules may need to change (e.g. backend P0 might be "no direct DB access" instead of "no hardcoded copy")
   ├─ Refresh the directory structure description
   └─ Update Eight-Step examples to match your discipline's scenarios

6. Update docs/prds/_template.md
   └─ Requirements document templates vary significantly by discipline; rewrite per discipline:
      Backend:  API definitions / error codes / rate limiting / SLA
      Data:     Metric definitions / data sources / lineage / refresh frequency
      Mobile:   Platform compatibility / distribution strategy / offline policy
      Design:   User goals / interaction flows / design principles
      Writing:  Audience / stance / outline / terminology

7. Do one end-to-end dry run
   ├─ Pick a minimal requirement
   ├─ Walk through /prd → /prd-check → /plan → /plan-check → /code → /test
   └─ Record any blockers immediately in docs/DECISIONS.md

8. Run /meta-audit once to verify framework coherence
```

---

## Part 6: What Not to Do

- ❌ **Extracting a "framework core + domain package" two-layer structure prematurely** — without running 2–3 disciplines first, you don't know where the truly universal boundary is; premature extraction almost always gets it wrong
- ❌ **Copying frontend rules directly to backend** — the files are still there but the content is wrong; AI will generate deliverables based on incorrect rules
- ❌ **Keeping unused modules** (e.g. leaving Design Token rules for a backend project) — empty shells are more misleading than nothing
- ❌ **Changing workspace without updating CLAUDE.md** — CLAUDE.md is the onboarding guide; stale onboarding pollutes all commands
- ❌ **Migrating all disciplines at once** — get one working first, refine it over 2–3 months, then fork for the next

---

## Part 7: Is Your Discipline a Good Fit for This Framework?

**Good fit**:
- Has a clear **requirements → breakdown → implementation → validation → delivery** flow
- Deliverables can be textualized, annotated with metadata, and anchored
- Has a "contract" concept (API / schema / token / glossary / review criteria)
- Team collaboration with traceability needs

**Poor fit** (or low ROI):
- Purely creative disciplines with highly non-linear processes (painting / composing)
- Deliverables that cannot be textualized or versioned
- Solo projects with no collaboration or traceability needs
- Requirements change so rapidly that documentation cost exceeds benefit

---

## Related Documents

- [README.md](../README.md) — Framework overview
- [WORKFLOW.md](WORKFLOW.md) — Eight-Step operations manual
- [DECISIONS.md](DECISIONS.md) — Architecture decision records (log migration decisions here)
- [.claude/README.md](../.claude/README.md) — Five-pack explained

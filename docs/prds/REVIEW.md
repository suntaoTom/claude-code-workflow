# PRD Manual Review Guide

> After `/prd` generates a draft, it must be reviewed by a human before running `/plan`. This document explains how to review and how to edit.
> Goal: Get the PRD through the hard gates in `/plan` while preventing downstream contamination.

---

## Why Review Is Required

When AI writes a PRD, uncertain areas are marked `[pending confirmation]` or `[default assumption]`. If these markers flow downstream:

```
PRD [pending confirmation]  →  task businessRules carry [pending confirmation]
                            →  source @rules carry [pending confirmation]
                            →  test it() assertions are placeholders — all fake
```

Therefore `/plan` has a hard gate at the entry: **a single `[pending confirmation]` anywhere in the document blocks it**. The core purpose of review is to zero out these markers.

---

## The Difference Between the Two Markers (Key)

| Marker | Meaning | Does `/plan` block? | How to handle |
|--------|---------|---------------------|---------------|
| `[pending confirmation]` | AI has no idea; a human must decide | ✅ Blocks | Must be cleared |
| `[default assumption]` | AI provided a sensible default | ❌ Does not block | Confirm at review meeting; no need to edit the body immediately |

Remember: **`[default assumption]` can stay as-is when running `/plan`** — finalize at the review meeting. `[pending confirmation]` must be fully resolved.

---

## Three-Step Review Process

### Step 1: Find all `[pending confirmation]` markers

Search with grep or your editor:

```bash
grep -n "\[pending confirmation\]" docs/prds/xxx.md
```

Note the hit count. The "Pending Confirmation Summary" at the end of the file is **navigation only** — the actual lines to fix are every hit in the body.

### Step 2: Make a decision for each one

Every `[pending confirmation]` is a decision, not just a text replacement. Three paths forward:

```
Should this rule / field / feature be built this iteration?
    ├─ Yes → Ask product/backend, get the answer, fill in the rule (see Approach 1)
    ├─ Not this iteration, but keep a placeholder → Note "implement next iteration", clear internal details (see Approach 2)
    └─ Not at all → Delete the entire section (see Approach 3)
```

### Step 3: Validate

After editing, run `/prd-check` for real-time self-validation (recommended):

```bash
/prd-check @docs/prds/xxx.md
```

It runs 5 checks at once (pending confirmation / pending fill-in / business rule placeholders / data contract status / 🆕 API stubs) and lists all unresolved issues. Fix one thing, run again, until you see:

```
✅ PRD completeness check passed
```

You can also quickly verify a single item with grep:

```bash
grep -n "\[pending confirmation\]" docs/prds/xxx.md
# No output = check 1 passed
```

---

## Approach 1: Fill In the Rule

The most common case. Use when "this needs to be built; AI just wasn't sure about the details."

### Example: Single-line field

Original:
```
| [pending confirmation] Email | string | [pending confirmation] | [pending confirmation] standard email format | - |
```

Ask product "does registration require an email?" — answer is "yes, required, with uniqueness validation" — update to:
```
| Email | string | Yes | Standard email format; uniqueness validated by backend | - |
```

**Key point**: Remove the `[pending confirmation]` prefix and make the content specific.

### Example: Business rule

Original:
```
6. [pending confirmation] Which specific pages are "admin-only" — product needs to define this
```

If the answer is "each feature PRD declares this itself," that is also a valid decision — rewrite as an affirmative statement:
```
6. This PRD defines only the permissions framework; which specific pages are "admin-only" is declared within each feature's own PRD permissions section — this PRD does not enumerate them
```

**Key point**: Even if the decision is "defer to downstream," the wording must be affirmative. The `[pending confirmation]` label must be gone.

---

## Approach 2: Not This Iteration — Keep a Placeholder

Use when "this feature will be built next iteration, but keep a reminder."

### Steps

**Add a note to the heading + clear all internal details**:

```markdown
## Feature X: Forgot Password (next iteration — not in this release)

> 📌 This feature will be started next iteration. Before kickoff, confirm: <list main open items>.
> It is not included in the current `/plan` breakdown; specific fields/rules/endpoints/error codes will be detailed in a new PRD.

---
```

**Note**: Updating just the heading is not enough! You must delete every `[pending confirmation]` occurrence in the section body — otherwise the gate will still block.

### Related items to clean up (easy to miss)

After updating the heading, search the full document for related content and clean it up too:

- The corresponding endpoint row in the "Endpoints Used" table
- Related error codes in the "Error Code Mapping" section
- Related stubs in the "API Proposal" section (at the end of the file)
- Any checklist items in the "Acceptance Checklist" that mention this feature
- Related entries in the "Summary" section

**Validation**: grep `[pending confirmation]` returns 0 hits, and a full-document search for the feature name (e.g., "forgot password") only appears in the retained heading.

---

## Approach 3: Not Building It — Delete the Entire Section

Use when "this won't be built and we don't need a placeholder."

Delete the entire section + remove all references to it (endpoints, error codes, summary, acceptance checklist).

If this feature is needed in a future iteration, create a standalone PRD (e.g., `docs/prds/forgot-password.md`) — cleaner than cramming it back in.

---

## How to Handle `[default assumption]`

**The body does not need to be changed** — you can run `/plan` as-is. However, two things are recommended:

1. **Add a summary at the end of the PRD** so the review meeting can approve them all at once:
   ```markdown
   ## Default Assumption Summary (to be confirmed at review meeting)

   - Account: 4–32 characters, letters/digits/underscore
   - Password: 8–32 characters, must contain letters and digits
   - ...
   ```

2. **After review approval, remove the `[default assumption]` labels from the body** (they become official rules). Leaving them doesn't block `/plan`, but removing them keeps the document cleaner.

---

## Common Mistakes

### Mistake 1: Only editing the summary section

The summary is navigation. Downstream consumers (task breakdown, test generation) read the **body**. Writing "confirmed" in the summary while `[pending confirmation]` still exists in the body → the gate still blocks, downstream still gets contaminated.

### Mistake 2: Only updating the heading to say "not in this iteration"

The heading is for humans. The gate does a **full-document string scan** — it doesn't understand semantics. Every literal `[pending confirmation]` in the body must be removed.

### Mistake 3: Replacing `[pending confirmation]` with `[TODO]` or `???`

The gate blocks these too. **Only affirmative rules or full deletion counts as passing.**

### Mistake 4: Guessing an answer and filling it in

The whole point of `[pending confirmation]` is "AI didn't dare guess." If you also guess and fill something in, you're planting a bug. **If you can't get the answer, don't build it** — don't make things up.

---

## Review Checklist

Check against this list after editing:

- [ ] grep `[pending confirmation]` returns zero hits
- [ ] Every feature either has complete rules or is explicitly marked "not in this iteration"
- [ ] For features not in this iteration, their related endpoints/error codes/summary entries are also cleaned up
- [ ] `[default assumption]` items are summarized at the end of the document (optional)
- [ ] The "Owner" field in Meta Information is filled in
- [ ] The "Changelog" has an entry for this review

All passing → run `/prd-check @docs/prds/xxx.md` to confirm green → then run `/plan @docs/prds/xxx.md`.

> 💡 `/plan` internally calls `/prd-check` as a prerequisite gate and terminates if it fails. Running `/prd-check` manually first gives you fast iterative feedback when fixing the PRD — so you don't need to trigger the full `/plan` on every attempt.

---

## Related Documents

- [_template.md](./_template.md) — PRD template
- [../WORKFLOW.md](../WORKFLOW.md) — Overall workflow
- [.claude/commands/plan.md](../../.claude/commands/plan.md) — Specific gate rules for `/plan`

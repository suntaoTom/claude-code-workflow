# Testing Guidelines

> This file defines **what to test and how to test it**. It does not cover execution workflows (that is the job of the `/test` command).

## Core Principle

**The sole source of test assertions is the `@rules` in the source file's JSDoc — not AI inference from reading the code.**

```
PRD business rules  →  @rules (JSDoc)  →  test it() assertions
    one-to-one, no skipping, no expanding
```

Violating this means tests will "test the current source code behavior" rather than "verify business rules" — when the source has a bug, the tests will be wrong too.

---

## Testing Tool Responsibilities

| Tool | Purpose | Location |
|------|---------|----------|
| Vitest | Unit tests / component tests (JSDOM) | `workspace/tests/` mirroring `workspace/src/` as `<name>.test.ts(x)` |
| Playwright | E2E tests / real browser interaction | `workspace/tests/e2e/*.spec.ts` |
| @testing-library/react | Component rendering + user interaction simulation | Used with Vitest |
| MSW (Mock Service Worker) | Intercept HTTP requests for mocking | `workspace/tests/mocks/` |

**How to choose**:

| Scenario | Use |
|----------|-----|
| Pure function logic (utils/) | Vitest unit test |
| Component rendering + click/input | Vitest + testing-library |
| Cross-component interaction / route navigation | Vitest + testing-library (still in JSDOM) |
| Real browser APIs (localStorage/IDB, etc.) | Vitest (JSDOM is sufficient) or Playwright |
| Cross-page flows (login → home → checkout) | Playwright E2E |
| Visual regression | Playwright screenshot (as needed) |

---

## Test File Location

All tests **go under `workspace/tests/`**, with a directory structure that **mirrors** `workspace/src/` one-to-one. Tests must not be placed in the same directory as source files or in `__tests__/` subdirectories.

```
workspace/src/features/login/components/LoginForm.tsx
workspace/tests/features/login/components/LoginForm.test.tsx   ← mirrors source path

workspace/src/features/login/hooks/useLogin.ts
workspace/tests/features/login/hooks/useLogin.test.ts

workspace/src/pages/list/index.tsx
workspace/tests/pages/list/index.test.tsx

workspace/tests/e2e/login-flow.spec.ts                          ← E2E in its own directory
workspace/tests/mocks/handlers.ts                               ← MSW handlers centralized
```

**Rules**:
- Unit/component tests: `workspace/tests/<src mirror path>/<name>.test.ts(x)`
- E2E tests all go in `workspace/tests/e2e/`, named `<flow>.spec.ts`
- MSW handlers centralized in `workspace/tests/mocks/`, split by module
- Test files importing business code **must use the `@/` alias** (e.g., `import SearchForm from '@/features/list/components/SearchForm'`); do not use relative paths like `../../../src/...`

**Why this structure** (see `docs/DECISIONS.md` entry 2026-04-20):
- `src/` contains only production code; bundler / tsc / coverage scans need no extra filtering
- Moving tests doesn't affect source file path stability
- CI uses a single path `workspace/tests/**` to run all tests with one command

---

## Mock Strategy

### Priority: real > fake, less > more

Use real implementations where possible (jsdom includes localStorage/URL and other Web APIs). Only mock when truly necessary (if the function signature matches, just run it directly).

### Categories

| Scenario | Tool | Reason |
|----------|------|--------|
| HTTP requests | **MSW** | Intercepts at the network layer; test code is unaware |
| Third-party modules (e.g., `umi`, `antd`) | **Do not mock** | Integration tests must test real behavior; mocking them defeats the purpose |
| Internal project modules (e.g., utils) | **Do not mock** | Just run them; mock only if there are real side effects |
| Time (new Date / setTimeout) | `vi.useFakeTimers()` | Deterministic time control |
| Random numbers / UUID | `vi.spyOn(Math, 'random')` | Deterministic |
| window.open / location.href | `vi.stubGlobal()` | JSDOM support for these is weak |

### Forbidden

- ❌ Manually writing `jest.mock('./xxx')` for entire modules — use MSW or run real code instead
- ❌ Mocking something and then asserting how many times the mock was called — usually you're testing the mock, not the business
- ❌ Mocking just to make a test pass — that means the test design is wrong, not that more mocking is needed

---

## Assertion Guidelines

### One `it()` per `@rules` entry

```typescript
/**
 * @rules
 *   - R1: Search button is disabled when phone number format is invalid
 *   - R2: Search button is disabled when all fields are empty
 *   - R3: Clicking reset clears all fields and triggers one automatic search
 */

// Test file
describe('SearchForm', () => {
  it('R1: Search button is disabled when phone number format is invalid', () => { ... });
  it('R2: Search button is disabled when all fields are empty', () => { ... });
  it('R3: Clicking reset clears all fields and triggers one automatic search', () => { ... });
});
```

- `it()` names **quote the rule verbatim**, with the R1/R2 number to match
- Each rule gets its own `it` — do not merge or split rules
- Assertions are the **technical translation** of the rule, not a rewrite of it

### Assertions must reflect what the user sees

```typescript
// ❌ Testing internal implementation (breaks when state/variable names change)
expect(wrapper.instance().state.submitDisabled).toBe(true);

// ✅ Testing what the user sees
expect(screen.getByRole('button', { name: 'Search' })).toBeDisabled();
```

### Query priority: `getByRole` > `getByLabelText` > `getByText` > `getByTestId`

- Role-based queries align with a11y semantics — writing tests also checks accessibility
- `getByTestId` is the last resort; requires adding `data-testid` to source code

---

## What Not to Test

- ❌ **TypeScript types** — tsc will catch errors; no need to test
- ❌ **Framework internals** — don't test whether React's useState triggered a re-render; that's React's job
- ❌ **Third-party library behavior** — don't test whether antd Button fires onClick when clicked
- ❌ **Implementation details** — whether a component uses useState or useReducer should not affect tests
- ❌ **Pure styles** — CSS correctness is verified by visual regression or human review, not assertions

---

## Coverage Goal

**Don't chase line coverage %; chase 100% `@rules` coverage.**

```
Are all @rules entries covered by a corresponding it()? ← This is the /test command's acceptance criterion
```

Line coverage is a byproduct:
- Components typically reach 70–80% line coverage (branch/edge coverage is the hard part)
- Utility functions should reach ~100% line coverage

---

## Test Failure Triage

When tests go red, check in this order — don't immediately change source code:

| Failure Type | Symptom | Action |
|-------------|---------|--------|
| **1. Test code is wrong** | selector not found / async not awaited | Fix the test code |
| **2. Environment misconfigured** | missing `@testing-library/jest-dom` / missing MSW handler | Fix the environment |
| **3. Test expectation is wrong** | AI guessed the expectation, doesn't match the rule | Fix the expectation (compare against `@rules` verbatim) |
| **4. Source code has a real bug** | rule says X, code does Y | **Fix the source** (only do this last) |

80% of failures are types 1–3, not type 4.

---

## Relationship to Other Rules

- No hardcoding ([no-hardcode.md](no-hardcode.md)): applies to test files too — don't hardcode copy strings (use i18n keys or constants)
- File documentation ([file-docs.md](file-docs.md)): `.test.ts(x)` files must also have a file header JSDoc; `@rules` may be omitted (tests don't carry business rules — assertions come from the tested file's `@rules`)

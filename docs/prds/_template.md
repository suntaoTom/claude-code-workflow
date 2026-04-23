# [Module Name] PRD

> Core principle for writing PRDs: **section headings are anchors**. All subsequent `@prd docs/prds/xxx.md#<anchor>` references rely on these headings to locate content.
> Therefore, heading names must be stable and unambiguous — do not rename them casually.

## Meta Information

| Field | Value |
|-------|-------|
| Module Code | `user-list` (English, matches the filename) |
| Owner | Jane Smith |
| Created | 2026-04-14 |
| Last Updated | 2026-04-14 |
| Status | draft / reviewing / approved / shipped |

## Background & Goals

> Why is this requirement being built? What problem does it solve? Who is the target user?
> Explain clearly in one paragraph, no more than 200 words.

## Glossary

> Fill in only when the module involves domain-specific terminology. Prevents misunderstanding by AI or new team members.

| Term | Definition |
|------|------------|
| Quota | The maximum number of API calls a user can make per month |

## Design Specs

> Design specs are the sole source of visual truth, complementing the business rules in the PRD: the PRD defines "what to build"; the design spec defines "what it looks like."
> Multiple source types can coexist — fill in whatever is available; leaving fields empty does not block progress.

| Field | Value |
|-------|-------|
| Source Type | link / file / mcp (multiple allowed) |
| Figma Link | `https://figma.com/file/xxx` (leave blank if none) |
| Local File | `docs/designs/xxx.png` or `docs/designs/xxx.sketch` (leave blank if none) |
| MCP Config | figma-mcp connected / not connected |

### Feature-to-Design Frame Mapping

> Maps each feature to the corresponding frame/page in the design spec, making it easier for `/plan` to break down tasks and `/code` to reference during implementation.

| Feature (PRD anchor) | Design Reference |
|----------------------|-----------------|
| #search-form | Figma: `<URL>#Frame-SearchForm` or `docs/designs/search-form.png` |
| #data-table | Figma: `<URL>#Frame-DataTable` |

> **Notes**:
> - Prefer Figma links (always point to the latest version); local files go stale
> - Once MCP is connected, `/code` can extract Design Tokens from Figma in real time — no manual export needed
> - Assets consumed directly by code (icons, image slices, etc.) should be exported to `workspace/public/images/`

---

## Feature 1: [Heading as Anchor]

> One second-level heading per feature; the heading itself is the anchor.
> e.g. `## Search Form` → `@prd docs/prds/user-list.md#search-form`

### User Story

> As a [role], I want [feature], so that [value].

### Field Definitions (for forms / data)

| Field | Type | Required | Validation | Default |
|-------|------|----------|------------|---------|
| Phone Number | string | No | 11 digits, starts with 1, second digit 3–9 | — |
| Status | enum | No | Enabled / Disabled / All | All |

### Business Rules (important — these are the source for test assertions)

> Every rule must be testable. Using "when... then..." phrasing improves clarity.
> Avoid describing technical implementation — write business semantics only.

1. When the phone number format is invalid, display an inline error message in real time and disable the search button
2. When all fields are empty, the search button is disabled
3. After the reset button clears all fields, one search is automatically triggered (the user does not need to click Search again)

### Data Contract (referencing OpenAPI)

> **Field details are defined by OpenAPI** (see `workspace/api-spec/openapi.json`). This section only covers **business-relevant information**: which endpoints are called, how error codes map to business behavior, and mock data conventions.
> Field types are defined once in OpenAPI; the frontend auto-generates `workspace/src/types/api.ts` via `pnpm gen:api` — no need to duplicate them here.

#### Endpoints Used

| Business Operation | operationId | Method | Path | Status |
|--------------------|-------------|--------|------|--------|
| Search users | `searchUsers` | GET | `/api/users/search` | ✅ Exists |
| View detail | `getUserById` | GET | `/api/users/{id}` | ✅ Exists |
| Export Excel | `exportUsers` | POST | `/api/users/export` | 🆕 Pending backend (see API proposal below) |

> **Status values**:
> - ✅ Exists: already defined in `workspace/api-spec/openapi.json`; use directly
> - 🆕 Pending backend: frontend has written a stub proposal; once reviewed, it goes into `workspace/api-spec/openapi.local.json` for local development until the backend implements it

> Field definitions, parameter constraints, and response structures → see the corresponding `operationId` in `workspace/api-spec/openapi.json` (or `workspace/api-spec/openapi.local.json`).

#### API Proposal (fill in only when there are 🆕 endpoints)

> The frontend writes an OpenAPI stub first. After frontend/backend review:
> - Place it in `api-spec/openapi.local.json` for local development (emergency fallback)
> - Or have the backend merge it directly into the main `openapi.json` (recommended — both sides share the same source from then on)

```yaml
# Example: export user list endpoint
paths:
  /api/users/export:
    post:
      operationId: exportUsers
      summary: Export filtered users as Excel
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                phone: { type: string }
                status: { type: string, enum: [enabled, disabled] }
      responses:
        '200':
          description: Excel file stream
          content:
            application/octet-stream:
              schema: { type: string, format: binary }
```

> ⚠️ After review approval, remember to change the status from 🆕 to ✅ so the frontend doesn't think it's still waiting on the backend.

#### Error Code Mapping (business-side definitions)

> OpenAPI only defines that error codes exist. **How to handle them is a business decision** and must be specified here.

| code | Meaning | Frontend Behavior |
|------|---------|-------------------|
| 0 | Success | — |
| 40001 | Invalid parameters | Inline form error message |
| 40301 | Unauthorized | Redirect to `/403` |
| 50001 | Server error | Auto-retry once; show toast on second failure |

#### Mock Data Conventions

- While the backend is not ready, write mock data in `workspace/mock/`. **You must import the generated types** to ensure structural alignment:
  ```typescript
  import type { paths } from '@/types/api';
  type SearchResp = paths['/api/users/search']['get']['responses']['200']['content']['application/json'];
  ```
- Switch to the real backend during integration testing via `workspace/config/proxy.ts`
- Never manually edit mock data when fields change — push the backend to update OpenAPI first, then pull the new JSON and let TypeScript compilation tell you what needs fixing

### Interaction Flow

> Text description or simple flow diagram.

```
User enters phone number → real-time validation → if valid, enable search button → click Search → loading → list updates
```

### Error Scenarios

| Scenario | Expected Behavior |
|----------|-------------------|
| API timeout | Show "Load failed, please retry" with a Retry button |
| Unauthorized | Redirect to `/403` |
| Empty data | Show antd `Empty` component |

---

## Feature 2: [Next Heading]

(Same structure as above)

---

## Acceptance Checklist (optional)

> Overall acceptance criteria before launch; integration requirements that span multiple features.

- [ ] The entire module displays correctly on Chrome, Safari, and mobile H5
- [ ] All endpoints have loading and error handling
- [ ] All i18n copy is complete (EN/ZH)

## Changelog

| Date | Change | Author |
|------|--------|--------|
| 2026-04-14 | Initial version | Jane Smith |

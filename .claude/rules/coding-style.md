# Coding Style

## Naming Conventions

- Components: PascalCase (UserProfile.tsx)
- Hooks: camelCase with `use` prefix (useUserData.ts)
- Utility functions: camelCase (formatDate.ts)
- Types/Interfaces: PascalCase, no `I` prefix (UserProfile, not IUserProfile)
- Constants: UPPER_SNAKE_CASE (MAX_RETRY_COUNT)
- Page files: placed under `pages/`, following Umi convention-based routing rules
- CSS: use CSS Modules (.module.less) or Ant Design token customization; no global style pollution

## Comment Guidelines

### Principle: Comments explain "why"; code explains "what"

Good naming and types are the best documentation — no need for comments that restate what the code does.

### When comments are required

1. **File header JSDoc** — every file must have one (see file-docs.md); this is the entry point for AI and new team members
2. **Business rules / domain logic** — the "why" behind the code; without it, no one will know
   ```typescript
   // Risk control requirement: daily withdrawal capped at 50,000; manual review required above that
   if (amount > DAILY_WITHDRAW_LIMIT) { ... }
   ```
3. **Non-obvious technical decisions** — workarounds, compatibility fixes, performance hacks
   ```typescript
   // antd DatePicker fires onChange twice on Safari; manually debounce
   const debouncedOnChange = useMemo(() => debounce(onChange, 0), [onChange]);
   ```
4. **TODO / FIXME / HACK** — mark known tech debt; must include a reason
   ```typescript
   // TODO(2026-Q2): remove this compatibility shim once backend v2 API launches
   // FIXME: race condition under concurrent access; temporarily mitigated with lock
   ```
5. **Regex / complex calculations** — without a comment, it's a riddle
   ```typescript
   // Chinese mainland phone number: starts with 1, second digit 3-9, 11 digits total
   const PHONE_REG = /^1[3-9]\d{9}$/;
   ```

### When comments are forbidden

1. **Restating the code** — the code already says it
   ```typescript
   // ❌ Set user name
   setUserName(name);

   // ❌ If admin
   if (role === ROLE.ADMIN) { ... }
   ```
2. **Commented-out code** — delete it; Git has the history
3. **Divider comments** — split into functions instead of `// ========= divider =========`
4. **Change logs** — don't write `// 2026-03-30 John changed xxx`; use Git log

### Comment format

- Single-line: use `//`, with a blank line between the comment and the code
- Multi-line: use `/** */` JSDoc style
- Keep comment language consistent throughout the project
- Comments must stay in sync with code; stale comments are worse than no comments

## Component Guidelines

- All components must use TypeScript functional components
- Props must define and export an interface
- Complex logic must be extracted into custom hooks
- Components are responsible for rendering only; no business logic inside
- Wrap pure presentational components with `React.memo`

## API Guidelines

- Use `@umijs/plugin-request` (umi-request) for all requests; do not introduce axios
- Define global request/response interceptors in the `request` config in `workspace/src/app.ts`
- Place request functions under `workspace/src/features/[module]/api/` or `workspace/src/services/`
- Keep type definitions consistent with the backend API documentation
- Handle error codes uniformly via the `errorHandler` config

## State Management Guidelines

- Prefer `@umijs/plugin-model` (useModel) for globally shared state; files go in `workspace/src/models/`
- Use `getInitialState` + `useModel('@@initialState')` for initialization data (user info, permissions, etc.)
- Use Zustand for complex, independent state; Store files begin with `use` (useAuthStore.ts)
- Use `useState`/`useReducer` for component-local state
- Never put server-cached data into global store

## Routing Guidelines

- Prefer Umi convention-based routing (the `pages/` directory structure is the route)
- Use `_layout.tsx` when layout nesting is needed
- Control route-level permissions via `@umijs/plugin-access` + `wrappers`
- Use the `[id].tsx` naming convention for dynamic routes

## Git Guidelines

- Commit message format: `type(scope): description`
- type: feat | fix | refactor | style | test | docs | chore
- Branch naming: feature/xxx, fix/xxx, refactor/xxx

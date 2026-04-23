# P0: No Hardcoding — Detailed Rules

> Priority: P0 — This rule takes precedence over all other coding conventions. Any code that violates it must not be committed.

## Core Principle

All values that may change must be introduced through config, constants, tokens, or i18n — never written directly into the code.
Config itself must not be heavily duplicated; reduce redundancy through hierarchical reuse.

## What Must Not Be Hardcoded

### 1. Copy & Internationalization
```typescript
// ❌ Forbidden
<Button>Submit</Button>
<span>No data</span>
message.success('Operation successful');

// ✅ Correct — via @umijs/plugin-locale i18n
<Button>{intl.formatMessage({ id: 'common.submit' })}</Button>
<span>{intl.formatMessage({ id: 'common.empty' })}</span>
message.success(intl.formatMessage({ id: 'common.success' }));
```

### 2. Colors & Styles
```typescript
// ❌ Forbidden
<div style={{ color: '#1890ff', fontSize: '14px' }} />
<Tag color="#f50">Error</Tag>

// ✅ Correct — via Ant Design Design Token
// Define tokens centrally in workspace/config/theme.ts
export const theme = {
  token: {
    colorPrimary: '#1890ff',
    fontSize: 14,
  },
};

// Use tokens in components
const { token } = theme.useToken();
<div style={{ color: token.colorPrimary, fontSize: token.fontSize }} />
<Tag color={token.colorError}>Error</Tag>
```

### 3. API URLs & Endpoints
```typescript
// ❌ Forbidden
fetch('/api/v1/users');
const BASE_URL = 'https://api.example.com';

// ✅ Correct — via config file + environment variables
// workspace/config/api.ts
export const API_ENDPOINTS = {
  USER_LIST: '/users',
  USER_DETAIL: (id: string) => `/users/${id}`,
} as const;

// baseURL controlled by environment variables, injected via proxy or define in workspace/config/config.ts
```

### 4. Business Constants & Enums
```typescript
// ❌ Forbidden
if (status === 1) { /* ... */ }
<Select options={[{ label: 'Enabled', value: 1 }, { label: 'Disabled', value: 0 }]} />

// ✅ Correct — via constants + lookup maps
// features/[module]/constants.ts
export const STATUS = { ENABLED: 1, DISABLED: 0 } as const;
export const STATUS_OPTIONS = [
  { label: 'status.enabled', value: STATUS.ENABLED },
  { label: 'status.disabled', value: STATUS.DISABLED },
] as const;
```

### 5. Sizes, Spacing & Breakpoints
```typescript
// ❌ Forbidden
<div style={{ padding: '16px 24px', maxWidth: '1200px' }} />

// ✅ Correct — via Design Token or CSS variables
// Defined in workspace/config/theme.ts
token: { padding: 16, paddingLG: 24, screenXL: 1200 }
```

### 6. Timeouts, Counts & Magic Numbers
```typescript
// ❌ Forbidden
setTimeout(fn, 3000);
if (list.length > 10) { /* pagination */ }

// ✅ Correct — extract into meaningful constants
const TOAST_DURATION_MS = 3000;
const PAGE_SIZE = 10;
```

## No-Duplication Rule for Config

Config itself must follow the DRY principle — avoid large amounts of repetition:

```
workspace/config/
├── theme.ts             # Single source of truth for theme tokens (colors/fonts/spacing)
├── constants/
│   ├── common.ts        # Global shared constants (page size / timeout / regex, etc.)
│   └── enums.ts         # Global shared enums + lookup maps
├── api.ts               # Centralized API endpoint management
└── config.ts            # Umi main config

workspace/src/features/[module]/
├── constants.ts         # Module-specific constants (values used only within the module)
└── ...
```

### Layered Reuse Principle

| Layer | Definition Location | Examples |
|-------|---------------------|---------|
| Theme tokens | workspace/config/theme.ts | Colors, fonts, border radius, spacing |
| Global constants | workspace/config/constants/ | Page size, date format, regex |
| Global i18n | workspace/src/locales/common.ts | Common copy (submit / cancel / confirm) |
| Module constants | workspace/src/features/[module]/constants.ts | Business status codes, dropdown options |
| Module i18n | workspace/src/locales/[module].ts | Module-specific copy |

### Forbidden

- Multiple modules each defining the same constant value → extract to `workspace/config/constants/`
- Multiple i18n files repeating the same copy → extract to `workspace/src/locales/common.ts`
- Defining the same token/color value in multiple places → consolidate in `workspace/config/theme.ts`

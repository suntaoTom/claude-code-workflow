# Tech Stack & Umi Conventions

## Tech Stack

- Framework: UmiJS 4.x + React 18 + TypeScript 5.x
- UI Library: Ant Design 5.x (integrated via @umijs/max)
- State Management: @umijs/plugin-model (lightweight) / Zustand (complex scenarios)
- Routing: Umi convention-based routing (auto-generated from file system)
- Requests: @umijs/plugin-request (built-in umi-request, based on fetch)
- Data Flow: @umijs/plugin-initial-state + useModel
- Build Tool: Umi Vite mode (configured via `vite: {}` in workspace/config/config.ts)
- Testing: Vitest + Playwright
- Linting: @umijs/lint (built-in ESLint + Prettier + Stylelint)
- Package Manager: pnpm
- i18n: @umijs/plugin-locale (enable on demand)

## Project Structure

```
workspace/                   # Frontend project root (UmiJS project)
├── config/
│   ├── config.ts            # Umi main config
│   ├── routes.ts            # Route config (if not using convention-based routing)
│   ├── proxy.ts             # Dev environment proxy config
│   └── theme.ts             # Ant Design theme customization
├── src/
│   ├── pages/               # Page components (Umi convention-based routing)
│   │   ├── index.tsx        # Home page /
│   │   ├── login/           # /login
│   │   │   └── index.tsx
│   │   └── [module]/        # Feature module pages
│   │       └── index.tsx
│   ├── features/            # Business logic organized by feature module
│   │   └── [module]/
│   │       ├── components/  # Module-specific components
│   │       ├── hooks/       # Module-specific hooks
│   │       ├── api/         # Module API request wrappers (based on umi-request)
│   │       ├── models/      # Module useModel data models
│   │       ├── stores/      # Module Zustand stores (complex state)
│   │       ├── types/       # Module type definitions
│   │       └── utils/       # Module utility functions
│   ├── models/              # Global data models (@umijs/plugin-model)
│   ├── components/          # Global shared components
│   ├── hooks/               # Global shared hooks
│   ├── services/            # Global API request wrappers
│   ├── utils/               # Global utility functions
│   ├── styles/              # Global styles
│   ├── types/               # Global type definitions
│   ├── access.ts            # Permission config (@umijs/plugin-access)
│   ├── app.ts               # Runtime config (getInitialState, layout, request)
│   └── global.less          # Global style entry
├── mock/                    # Mock data (Umi built-in mock support)
├── public/                  # Static assets
├── api-spec/                # OpenAPI contract files
├── scripts/                 # Build/generation scripts
├── tests/                   # Test files
├── package.json
└── tsconfig.json
```

## Ant Design Component Library

Ant Design 5.x is integrated via @umijs/max. The following components are imported directly from `antd` — do not re-wrap them:

- Button, Input, Select, Checkbox, Radio, Switch, DatePicker
- Modal, Drawer, Popover, Tooltip, Popconfirm
- Table (supports sorting/pagination/filtering), ProTable (advanced table)
- Form + Form.Item (built-in validation), ProForm (advanced form)
- message / notification (global alerts)
- Card, Badge, Tag, Avatar, Descriptions
- Skeleton, Spin, Empty, Result
- Layout, Menu, Breadcrumb, Tabs
- Upload, Tree, Transfer, Cascader

If a custom wrapper is needed, place it under `workspace/src/components/` and document the reason in the directory README.md.

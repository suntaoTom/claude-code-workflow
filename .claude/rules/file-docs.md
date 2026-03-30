# 文件与模块说明规范

> 目的: 让任何 AI 模型或开发者接手项目时，能快速理解每个目录和文件的作用，降低维护成本。

## 核心规则

**每次创建或修改代码文件时，必须同步维护所在目录的 `README.md`。**

## 目录级 README.md

每个功能目录（components/, hooks/, stores/, utils/, api/, types/）都必须有一个 `README.md`，格式如下：

```markdown
# 目录名称

> 一句话描述这个目录的职责

## 文件清单

| 文件名 | 说明 | 依赖 | 最后更新 |
|--------|------|------|----------|
| UserProfile.tsx | 用户资料展示组件，支持编辑模式 | useUserData, UserAvatar | 2026-03-30 |
| UserCard.tsx | 用户卡片缩略组件 | Avatar (antd) | 2026-03-30 |

## 模块关系

> 简要描述本目录内文件之间、以及与其他模块的依赖关系
```

## 功能模块级 README.md

每个 `src/features/[module]/` 目录必须有一个顶层 `README.md`，格式如下：

```markdown
# 模块名称

> 模块的业务功能描述

## 子目录结构

| 目录 | 说明 |
|------|------|
| components/ | 模块专属 UI 组件 |
| hooks/ | 模块数据逻辑 hooks |
| api/ | 后端接口请求封装 |
| stores/ | Zustand 状态管理 |
| types/ | TypeScript 类型定义 |
| utils/ | 模块工具函数 |

## 核心业务流程

> 用文字或简单流程描述核心逻辑，例如：
> 用户登录 → 调用 api/login → store 存 token → 跳转首页

## 对外暴露

> 列出本模块向外导出的主要组件、hooks、类型，供其他模块引用
```

## 文件头部注释

每个代码文件顶部必须包含说明注释：

```typescript
/**
 * @description 用户资料展示组件，支持查看和编辑两种模式
 * @module features/user/components
 * @dependencies useUserData, useAuthStore, Avatar (antd)
 * @example
 *   <UserProfile userId="123" editable />
 */
```

对于不同类型的文件，注释需包含：

- **组件**: description, module, dependencies, props 说明, example
- **hooks**: description, module, params, returns, example
- **stores**: description, module, state 字段说明, actions 说明
- **utils**: description, module, params, returns, example
- **api**: description, module, 请求方法, 请求路径, params, returns
- **types**: description, module, 各字段说明

## 触发时机

以下操作必须同步更新对应 README.md：

1. **新建文件** → 在目录 README.md 的文件清单中新增一行
2. **删除文件** → 从目录 README.md 中移除对应行
3. **重命名文件** → 更新 README.md 中的文件名
4. **修改文件职责** → 更新 README.md 中的说明列
5. **新建功能模块** → 创建模块级 README.md
6. **修改模块依赖关系** → 更新模块间关系描述

## 全局索引

在 `src/README.md` 中维护一个项目整体索引：

```markdown
# 项目模块索引

## 功能模块 (features/)

| 模块 | 说明 | 状态 |
|------|------|------|
| user | 用户管理（登录/注册/资料） | 开发中 |
| dashboard | 数据看板 | 已完成 |

## 全局通用

| 目录 | 说明 |
|------|------|
| components/ | 通用 UI 组件 |
| hooks/ | 通用 hooks |
| lib/ | 第三方库封装 |
| types/ | 全局类型定义 |
```

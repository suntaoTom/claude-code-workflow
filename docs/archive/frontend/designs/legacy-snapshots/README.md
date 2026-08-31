# 旧版本实现截图归档

> 迁移类需求起草 PRD 时, 把旧版本的关键页面截图存档在这里, 作为「行为参考来源」。
> 与 `screenshots/` (新设计稿) 互补: 新设计稿管「长什么样」, 旧版本截图管「旧版当前怎么做的」。

## 适用场景

凡是基于已有系统重构 / 迁移 / 升级的需求, 都该有这层归档:

- H5 / Web Clip → 原生 App (React Native / Flutter)
- jQuery 老站 → React / Vue / Umi
- 老版本 Vue 2 → Vue 3 / Composition API
- AngularJS → 现代框架
- 老 React Class 组件 → Hooks 重构

全新业务 / 内部重构 (没有旧版本对应页面) 可跳过本目录。

## 为什么需要

旧版本可能在迁移期间继续迭代或最终下线, 但 PRD 是基于「当时那个旧版」写的业务规则。
存档截图保证: 即使旧版改了/下线了, 评审 PRD / 排查行为差异时仍能回到原始状态。

## 命名规则

- `<模块>-<页面>.png` 或 `<模块>-<页面>-<状态>.png`
- 示例:
  - `user-profile.png` — 个人中心首页
  - `user-email-bind.png` — 修改绑定邮箱页
  - `user-email-bind-error.png` — 邮箱页错误态
  - `order-list.png` — 订单列表
  - `order-list-empty.png` — 订单列表空态

## 在 PRD 里怎么引用

PRD 功能点的「信息源对照」段:

```markdown
| 📜 旧版本实现 | docs/designs/legacy-snapshots/user-email-bind.png |
```

也可以同时填 URL + 本地截图 (URL 永远指向最新, 截图是定格):

```markdown
| 📜 旧版本实现 | https://legacy.example.com/profile/email-bind  +  docs/designs/legacy-snapshots/user-email-bind.png |
```

## 不要做的事

- ❌ 把截图当成视觉规范的来源 — 视觉看 `screenshots/` (新设计稿)
- ❌ 在代码里写 `@legacy` 字段 — 代码不直接对旧版负责, 旧版行为已经被 PRD 翻译成 `@rules` 了
- ❌ 长期补存量截图 — 只存当前迁移类 PRD 实际用到的页面, 不追求旧版全站归档

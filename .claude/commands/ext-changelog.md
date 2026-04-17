你现在是代码变更分析师。对指定文件或目录生成可读的变更影响报告, 帮助理解一段时间内发生了什么。

## 与 /release 的区别

- `/release` — 面向**发布**, 输出结构化 changelog, 用于 tag/发版
- `/ext-changelog` — 面向**理解**, 输出人可读的变更故事, 用于周报/交接/复盘

## 输入

| 输入 | 示例 | 行为 |
|------|------|------|
| 无参数 | `/ext-changelog` | 最近 7 天的所有变更 |
| 时间范围 | `/ext-changelog --since 2026-04-10` | 指定起始日期 |
| 目录 | `/ext-changelog workspace/src/features/login/` | 只看某个模块的变更 |
| 作者 | `/ext-changelog --author alice` | 只看某人的变更 |

## 输出格式

```markdown
# 变更报告: 2026-04-10 → 2026-04-17

## 概要
本周主要完成了登录模块开发, 修复了 3 个 bug, 重构了鉴权逻辑。

## 按模块拆解

### login (12 commits, 5 文件新增, 3 文件修改)
- 新增账号密码登录 + 记住我功能
- 新增登录表单组件、鉴权 hook、API 封装
- PRD: docs/prds/login.md

### auth (3 commits, 2 文件修改)
- 重构: 提取公共鉴权逻辑到 useAuth hook
- 影响范围: login, register 模块都在用

## Bug 修复
- 修复 Dashboard 白屏 (login token 过期未跳转)
- 修复记住我 token 未延长有效期
- 修复按钮 hover 颜色硬编码

## 风险点
- auth 模块重构后, register 页面还没回归测试
- login.md PRD 中 [待确认] 项仍有 2 处

## 统计
- 总 commit: 18
- 新增文件: 7
- 修改文件: 11
- 活跃贡献者: 2 (alice, bob)
```

## 执行逻辑

1. `git log --since=<日期> --name-status` 获取变更文件列表
2. 按目录/模块分组
3. 读 commit message 提取 type/scope/description
4. 关联 PRD / 任务 / Bug 报告
5. 识别风险点 (大面积修改 / 未测试 / 有 [待确认])
6. 生成可读报告

## 使用方式

```
/ext-changelog                                    # 本周变更
/ext-changelog --since 2026-04-01                  # 本月变更
/ext-changelog workspace/src/features/login/       # 登录模块变更
/ext-changelog --author alice --since 2026-04-14   # Alice 最近 3 天的产出
```

请生成变更报告:
$ARGUMENTS

# Claude Code GitHub Action 接入指南

> 把 Claude Code 装进任意 GitHub 仓库, 在 issue / PR 评论 `@claude xxx`, AI 自动改代码 + 开 PR。
>
> 本文档基于 spider 仓库实战经验整理, 包含官方文档没说清楚的踩坑点。复制到其他项目仓库直接照做即可。

> **本仓库已有更严格的接入方案** (`@claude fix` slash command + draft PR), 见 [.github/SETUP.md](../.github/SETUP.md)。
>
> | 方案 | 触发词 | 用法 | 适合 |
> |---|---|---|---|
> | **本仓库现有方案** | `@claude fix` | 调用 `/fix --headless --pr` slash command, 严格白名单, 强制 draft PR | bug 修复流水线 |
> | **本文档介绍的通用方案** | `@claude` | 直接读 issue 描述自由发挥, 范围更广 | 加 feature / 改文档 / 重构 / 一般任务 |
>
> 两者可以共存 (不同触发词 + 不同 workflow 文件)。本文档作为「面向新仓库」的通用接入手册保留。

---

## 0. 你将得到什么

接入完成后:

- 在 issue 描述里写 `@claude 帮我修 xxx`, AI 自动读代码 → 改代码 → 开 PR
- 在 PR 评论里写 `@claude 这里换种实现`, AI 在同一 PR 上追加 commit
- PR 由你**人工 review 后合并**, AI 不会自动 merge
- 仓库 owner / collaborator 才能触发, 防陌生人刷 API 余额

## 1. 准备清单 (提前备好)

| 项目 | 必需? | 拿不到怎么办 |
|---|---|---|
| **目标 GitHub 仓库** | ✅ | — |
| **Anthropic 账号** + Claude Pro 订阅 或 API credit | ✅ | https://claude.ai 订阅 / https://console.anthropic.com 充值 |
| **本地装好 Node.js** (用 Homebrew 或 nvm, 不要用 IDE 自带的) | ✅ (只为生成 OAuth token) | `brew install node` |
| 仓库的 admin 权限 | ✅ | 不是 owner 进不了 Settings |

> **Pro vs API 计费选哪个**:
> - Pro/Max ($20-$100 月费): 用 OAuth token, 不额外烧钱, 但有 5 小时滚动限流
> - API key: 按 token 用量, 没限流但需要预付 credit
> - 个人小项目偶尔触发 → Pro; 团队 / 高频 → API key
> - 两个都配, workflow 会优先用 OAuth (本指南默认这样)

---

## 2. 五步接入 (按顺序)

### 步骤 1: 生成 Claude OAuth Token (Pro/Max 用户走这条)

本地终端:

```bash
# 装 Claude Code CLI (用 Homebrew 的 npm, 别用 IDE 自带的, 会撞权限)
/opt/homebrew/bin/npm install -g @anthropic-ai/claude-code

# 生成长期 token
claude setup-token
```

浏览器自动打开 → 用 Pro 账号登录授权 → 终端输出形如 `sk-ant-oat01-xxxxxxxxx...` 的一长串 token。

**复制时三个坑**:
- ❌ 不要带前后空格
- ❌ 不要带引号 `"` `'`
- ❌ 不要把终端的换行符也复制进去 (整段 token 是**一整行**, 没换行)

> **如果你只想用 API key (按量付费)**, 跳过这一步, 去 https://console.anthropic.com/settings/keys 创建一个 key 即可。

### 步骤 2: 添加为 GitHub Secret

打开 `https://github.com/<你的用户名>/<仓库名>/settings/secrets/actions`

点 **New repository secret**, 填:

| 字段 | 填什么 |
|---|---|
| **Name** | `CLAUDE_CODE_OAUTH_TOKEN` (用 OAuth) 或 `ANTHROPIC_API_KEY` (用 API key) |
| **Secret** | 粘贴上一步的 token / key |

⚠️ **Name 必须**完全一致 (区分大小写)。命名错了 workflow 找不到, 会报 `Either ANTHROPIC_API_KEY or CLAUDE_CODE_OAUTH_TOKEN is required`。

### 步骤 3: 安装 Claude GitHub App

打开 https://github.com/apps/claude → **Install** → 选目标仓库 (或 All repositories) → 授权。

确认安装成功: https://github.com/settings/installations 里能看到 Claude。

> 没装这一步, workflow 跑起来会因为没权限失败。

### 步骤 4: 打开仓库的 PR 创建权限

打开 `https://github.com/<你的用户名>/<仓库名>/settings/actions`

往下滚到 **Workflow permissions**, **勾上**:

> ☑ Allow GitHub Actions to create and approve pull requests

点 Save。

⚠️ 这步**最容易忘**。没勾这个 workflow 哪怕 `permissions` 字段全开, 创建 PR 还是会被 GitHub 拒掉。

### 步骤 5: 创建 workflow + 守则文件

在仓库根目录创建两个文件:

#### 5a. `.github/workflows/claude.yml`

```yaml
name: Claude Code

on:
  issue_comment:
    types: [created]
  pull_request_review_comment:
    types: [created]
  issues:
    types: [opened, assigned]
  pull_request_review:
    types: [submitted]

jobs:
  claude:
    # 只允许仓库 owner 和 collaborators 触发, 防止陌生人刷 API 余额
    if: |
      (github.event_name == 'issue_comment' && contains(github.event.comment.body, '@claude')) ||
      (github.event_name == 'pull_request_review_comment' && contains(github.event.comment.body, '@claude')) ||
      (github.event_name == 'pull_request_review' && contains(github.event.review.body, '@claude')) ||
      (github.event_name == 'issues' && (contains(github.event.issue.body, '@claude') || contains(github.event.issue.title, '@claude')))
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
      issues: write
      id-token: write
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Run Claude Code
        uses: anthropics/claude-code-action@v1
        with:
          # 优先用 Pro/Max 订阅的 OAuth token, 没有再回退到 API key 按量计费
          claude_code_oauth_token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          # 模型 + 工具白名单 (放行 git + gh 命令, 但禁掉 gh pr merge)
          claude_args: >-
            --model claude-opus-4-7
            --allowedTools "Bash(git:*),Bash(gh pr create:*),Bash(gh pr edit:*),Bash(gh pr comment:*),Bash(gh pr view:*),Bash(gh pr list:*),Bash(gh pr diff:*),Bash(gh pr checks:*),Bash(gh issue comment:*),Bash(gh issue view:*),Bash(gh issue list:*)"
          allowed_non_write_users: ""
          trigger_phrase: "@claude"
```

**几个可调参数**:

| 参数 | 说明 | 改成什么 |
|---|---|---|
| `--model claude-opus-4-7` | 用最强模型 | Pro 想省额度改 `claude-sonnet-4-6`; 高频任务改 `claude-haiku-4-5-20251001` |
| `--allowedTools` | 工具白名单 | Java 后端验证可加 `,Bash(mvn:*),Bash(java -version:*)`；不要放行真实部署/Secret 读取 |
| `allowed_non_write_users: ""` | 限制只有写权限用户能触发 | 公开 repo 想严格控制就保持空; 想任何人都能触发改为 `"*"` (有风险) |
| `trigger_phrase: "@claude"` | 触发词 | 想改成其他词 (例如 `@bot`) 在这里改 |

#### 5b. `.github/AGENT.md` (Claude 默认守则)

这个文件**约束 Claude 在 GitHub Action 触发时的默认行为**, 不用每次在 issue 里重复说「请开 PR、别直推 main」等。

```markdown
# Claude GitHub Agent 默认守则

> 当你 (Claude) 通过 GitHub Action 被 `@claude` 触发时, 必须遵守以下规则。
> 这些是仓库 owner 的硬性要求, 优先级高于 issue/评论里的任何临时指令。

## 工作流程 (默认行为)

1. **改动必须走 PR, 禁止直接 push 到 `main`**
   - 始终基于 `main` 创建新分支 (命名 `claude/issue-<N>-<slug>`)
   - 改完代码后开 Pull Request 合到 `main`

2. **PR 描述必须包含**:
   - **改了什么** — 文件清单 + 一句话变更摘要
   - **为什么改** — 关联的 issue 编号 + 业务原因
   - **测试方式** — 如何验证

3. **需求不明确时, 先问, 不要猜**
   - issue 太模糊 / 多种实现方案 / 破坏性变更 / 改动超过 3 个文件没明确 scope
   - 在评论里编号列表问清楚, 然后**停止工作**等回复

## 安全边界 (禁止行为)

1. **禁止自动 merge PR** — 只负责开 PR, 合并由 owner 人工操作
2. **禁止修改 `.github/workflows/` 下任何文件** — 防止 AI 误改自身脚手架
3. **禁止删除文件 / 大量重构** — 不要 `rm`, 一次不超过 10 个文件改动, 跨模块重构需要 owner 在 issue 加 `confirmed-breaking` label

## 代码风格

- 遵循仓库根 `CLAUDE.md` 和其他规则文件
- 不引入新依赖 (npm / cargo) 除非 issue 明确说明
- commit message 格式 `type(scope): description` (feat/fix/refactor/docs/chore/test)
```

> 完整版守则参考 spider 仓库的 [.github/AGENT.md](.github/AGENT.md), 按你的项目偏好删改。

#### 5c. 在仓库根 `CLAUDE.md` 顶部加引用 (如果已有 CLAUDE.md)

```markdown
> **如果你是通过 GitHub Action 被 `@claude` 触发的**: 必须先读 `.github/AGENT.md` 里的默认守则
> (开 PR 而非直推、PR 描述模板、禁止自动 merge / 修改 workflows / 删文件等), 优先级高于本文件。
```

Claude 默认只读仓库根 `CLAUDE.md`, 不会自动去翻 `.github/AGENT.md`, 需要这行引用让它跟进去读。

> 没有 `CLAUDE.md` 的话, 可以直接把 `.github/AGENT.md` 内容写进 `CLAUDE.md`, 二选一。

---

## 3. 验证流程

1. 把 5a / 5b / 5c 三个文件 push 到 main
2. 打开 `https://github.com/<你>/< repo>/issues/new` 建一个测试 issue:
   ```
   标题: 测试 Claude
   正文: @claude 请在仓库根目录创建 HELLO.md, 内容写「Hello」, 然后开 PR
   ```
3. 提交后回到 Actions 标签页, 应该有一条新的 "Claude Code" workflow 运行
4. 等 30 秒~几分钟, Claude 在 issue 里回复进度
5. 去 Pull requests 页面应该能看到 Claude 开的新 PR
6. review PR 内容 → 点 **Merge pull request** 合并

---

## 4. 常见错误 + 修法 (踩过的坑)

### 错误 1: `Either ANTHROPIC_API_KEY or CLAUDE_CODE_OAUTH_TOKEN is required`

**原因**: Secret 名字写错了, 或者根本没添加。

**修法**:
1. 去 `https://github.com/<repo>/settings/secrets/actions` 检查
2. 名字必须**精确**为 `CLAUDE_CODE_OAUTH_TOKEN` 或 `ANTHROPIC_API_KEY`, 区分大小写
3. 不要叫 `spider` `my_key` 等自定义名字 (除非同步改 workflow 里的 `${{ secrets.XXX }}` 引用)

### 错误 2: `Credit balance is too low`

**原因**: 用的是 API key 模式但账户没充值。

**修法**:
1. 去 https://console.anthropic.com/settings/billing 充至少 $5
2. **同时建议**在 https://console.anthropic.com/settings/limits 设月度上限, 例如 $20/月
3. 或者切到 OAuth Token 模式 (步骤 1)

### 错误 3: `Header '14' has invalid value: '***'`

**原因**: OAuth token 粘贴时带了空格 / 换行 / 引号 / 不完整。

**修法**:
1. 重新跑 `claude setup-token` 生成新 token
2. 整段一次性选中复制 (注意终端如果是换行模式可能会插入换行符)
3. 在 GitHub Secret 编辑框里**先清空再粘贴**, 检查右侧没显示 "Line 2"

### 错误 4: workflow 显示 "Skipped" 跳过

**原因**: issue 标题 / 正文里**没有** `@claude` 触发词, 但触发了 `on: issues:` 事件。

**修法**:
- 重新建 issue 时把 `@claude` 写在正文 (不要只在标题)
- 或者在已有 issue 下评论 `@claude xxx` 触发

### 错误 5: workflow 成功但没开 PR

**原因 A**: Claude 任务太模糊 (例如「再试一次」「修一下」), 它只回复没改代码。
**修法**: 评论里写具体任务 (哪个文件、什么改动、期望结果)。

**原因 B**: 仓库 Settings → Actions → Workflow permissions 没勾「Allow GitHub Actions to create and approve pull requests」。
**修法**: 步骤 4 的勾选框去打勾。

**原因 C**: Claude 提示「需要把 `gh pr create` 加入 `--allowedTools`」。
**修法**: workflow 里的 `claude_args` 必须包含 `Bash(gh pr create:*)` (本指南的模板已包含)。

### 错误 6: npm 全局安装 EPERM 权限错误

**现象**:
```
EPERM: operation not permitted, mkdir '/Applications/DevEco-Studio.app/Contents/tools/node/lib/node_modules/...'
```

**原因**: 系统 PATH 里 IDE 自带 Node (如 DevEco Studio / VSCode 内置) 排在前面, 装在 `/Applications/` 系统目录写不进去。

**修法**: 用 Homebrew 的 npm 绕开:
```bash
/opt/homebrew/bin/npm install -g @anthropic-ai/claude-code
```

长期方案: 修 `.zshrc` 让 `/opt/homebrew/bin` 在 PATH 前面, 或者用 nvm 管理 Node 版本。

---

## 5. 给 Claude 任务的最佳实践

| ❌ 模糊 (Claude 会反问或瞎猜) | ✅ 明确 (Claude 直接动手) |
|---|---|
| `@claude 修一下` | `@claude TopBar.tsx:42 的 z-index 改成 999 并开 PR` |
| `@claude 优化性能` | `@claude 首屏加载 3.2s 太慢, 请检查 src/main.tsx 的同步 import, 改成路由级懒加载` |
| `@claude 加缓存` | `@claude 给 features/scan/useWorkspaceScan.ts 加 LRU 缓存, 上限 50, TTL 5 分钟` |
| `@claude 重构这块` | `@claude 把 TopBar.tsx 里的搜索逻辑抽到 useSearch.ts hook, 组件只保留渲染` |

**写任务时的清单**:
- [ ] 提到具体文件路径或模块名
- [ ] 说清楚现状 / 问题 / 期望表现
- [ ] 涉及多个方案时, 自己先选一个 (或让 Claude 给方案后再确认)
- [ ] 涉及破坏性变更 (删字段 / 改 API) 时明确说「这是破坏性变更, 请慎重」

---

## 6. 成本与额度

### Pro 订阅 ($20/月) 用 OAuth Token

- 默认走 Sonnet 4.6, 5 小时滚动额度 (大约 50~200 次中型对话)
- 用 Opus 4.7 会消耗更多额度, 撞限流就几小时不可用
- **建议**: 默认 Sonnet, 复杂任务在 issue 评论里加 `--model claude-opus-4-7` 临时切

### API Key 按量付费

| 模型 | 输入 ($/M token) | 输出 ($/M token) | 单次 issue 估算成本 |
|---|---|---|---|
| Opus 4.7 | $15 | $75 | $0.10~$1.00 |
| Sonnet 4.6 | $3 | $15 | $0.02~$0.20 |
| Haiku 4.5 | $1 | $5 | $0.005~$0.05 |

**建议**: 月度消费上限设 $20-$50, 防止恶意触发或循环 bug 把余额烧光。

---

## 7. 安全清单 (上线前检查)

- [ ] Secret 是 `CLAUDE_CODE_OAUTH_TOKEN` 或 `ANTHROPIC_API_KEY`, 不是泄露过的旧 key
- [ ] 之前不小心泄露的 key 已经在 console 吊销 (https://console.anthropic.com/settings/keys)
- [ ] `allowed_non_write_users: ""` 限制了只有 owner/collaborator 能触发 (公开仓库尤其重要)
- [ ] `--allowedTools` 没放 `gh pr merge` `gh repo delete` 等危险命令
- [ ] `.github/AGENT.md` 明确禁止 Claude 修改 workflow 自身
- [ ] Anthropic console 设了月度消费上限 (https://console.anthropic.com/settings/limits)
- [ ] `.github/workflows/claude.yml` 没有任何明文 key (只用 `${{ secrets.XXX }}`)

---

## 8. 跨仓库复用速查

把这个仓库的下面 3 个文件复制到新仓库:

```
.github/workflows/claude.yml   # workflow 配置
.github/AGENT.md                # 默认守则
docs/SETUP_CLAUDE_GITHUB_ACTION.md   # 本文档 (可选)
```

然后**逐项做**:

| 步骤 | 在哪做 | 耗时 |
|---|---|---|
| 1. 生成 / 复用 OAuth token | 本地终端 | 1 min (复用已有则 0) |
| 2. 添加 GitHub Secret | 仓库 Settings → Secrets | 30 sec |
| 3. 安装 Claude App | https://github.com/apps/claude | 1 min |
| 4. 勾选「允许 Actions 创建 PR」| 仓库 Settings → Actions | 10 sec |
| 5. push workflow + AGENT.md | git | 1 min |
| 6. 建测试 issue 验证 | GitHub UI | 3 min |

**总耗时**: 全新仓库约 5-10 分钟; 已有 token 的新仓库约 3 分钟。

---

## 9. 参考资料

- 官方 Action 仓库: https://github.com/anthropics/claude-code-action
- Claude Code CLI 文档: https://docs.claude.com/claude-code
- Anthropic API 文档: https://docs.claude.com/api
- 计费 / 限额: https://console.anthropic.com/settings/billing
- 模型清单: https://docs.claude.com/claude/docs/models-overview

---
description: 前端开发工程师 — 按 tasks.json 顺序实现代码, 支持 --from / --only 参数
argument-hint: @docs/tasks/tasks-xxx.json [--from T005] [--only T003,T004]
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, TodoWrite
idx: 3
gate: plan-check
inputs: ["tasks.json"]
outputs: ["src/*.ts"]
---

你现在是前端开发工程师角色。请按指定的 tasks.json 顺序实现代码。

## 输入

- `@docs/tasks/tasks-xxx.json` 路径 → 直接读取
- 不带路径 → 停下询问: 「请指定任务清单路径, 例: /code @docs/tasks/tasks-login-2026-04-15.json」
- 带 `--from T005` 参数 → 从指定 taskId 开始 (用于中断后续跑)
- 带 `--only T003,T004` 参数 → 只执行指定任务 (用于局部返工)

## 第零步: 前置校验 (不通过直接停)

按顺序执行, 任一不通过都报错终止:

1. **硬性闸门: 调用 `/plan-check`** — 对输入的 tasks.json 跑一遍 `.claude/commands/plan-check.md` 定义的 6 项检查 (含结构 / 依赖 / 追溯 / API 契约 / 顺序 / PRD 漂移)。不通过直接输出 `/plan-check` 的报错内容并终止, 不进入编码

   `/plan-check` 内部已经包含了 `/prd-check` 的 PRD 完备性校验, 不需重复调用

2. **openapi.json 类型已生成** — 检查 `workspace/src/types/api.ts` 存在; 不存在先跑 `pnpm gen:api`
3. **无未处理 blocked 任务** — 如果 tasks[] 里有 `status: "blocked"` 的任务 (如「推动后端更新 OpenAPI: ...」), 停下列出, 要求用户决定是否跳过

## 第零点五步: 断点恢复 (处理上次中断的状态)

扫一遍 tasks.json 的 status 分布, 按以下规则决定起点:

| 状态 | 动作 |
|------|------|
| `done` | 自动跳过, 不重做 |
| `pending` | 按依赖顺序, 从第一个「上游全 done」的 pending 任务开始 |
| `in-progress` | **停下问用户** (见下) |

### 遇到 `in-progress` 任务时

说明上次会话在这个任务里中断了, 文件状态未知, 直接续写有风险 (可能已部分写入、可能只改了 status 还没动代码)。不要自行判断, 先给用户列出现状:

1. 读 `task.filePath`, 确认文件是否已存在
2. 若存在, 读文件头 JSDoc 看 `@rules` 是否覆盖了本任务 `businessRules` 全部条目
3. 简报一句: 「T00X 文件 [已存在/不存在], JSDoc [完整/缺 N 条规则/无]」
4. 给用户 4 个选项, 等待选择:
   - **(A) 继续补全** — 文件已部分写入, 基于现状补完剩余逻辑, 不推翻已有代码
   - **(B) 删除重做** — 已有代码偏离规则或质量差, 删文件从头写
   - **(C) 标记为 done** — 实际已写完, 只是上次没来得及改状态, 直接置 done 跳过
   - **(D) 回退为 pending** — 之前没真正动代码, 改回 pending 按正常流程重跑

多个 `in-progress` 时逐个询问, 不要一次性批处理 (每个文件状态可能不同)。

### 带 `--from` / `--only` 参数时

跳过本步, 按参数直接定位起点 (用户已明确指定了断点, 不必再询问)。

## 执行原则

### 按依赖顺序执行, 但**独立任务并行**(不是一根筋串到底)

> 见 [`.claude/rules/concurrency.md`](../rules/concurrency.md)。`tasks.json` 的 `dependencies`
> 就是依赖图 —— 不要把所有任务排成一条线串行做, 互不依赖、改的不是同一文件的任务**并行 spawn subagent**。

执行策略(开干前先算一次):

1. **拓扑分层** — 按 `dependencies` 把任务排成「层」, 同层内互不依赖(上游全 `done` 才进下一层)。
2. **层内分组** — 同层里再按 `filePath` 不重叠分组 → 每组可并行。
   - 例:两个独立模块的 `types` 文件无依赖边、不同文件 → **并行**。
   - 反例:一条 `types→hook→component→page` 链 → 链内**串行**;但多条独立模块链之间**并行**。
3. **并行 spawn** — 一层里可并行的任务, **在同一条消息里发多个 `Agent` 调用**, 真并发。
   每个 subagent **只写自己 task 的源文件**, 回报「要加的 README 行 / i18n key / 路由项 / index 导出」。
4. **串行收口(主 agent 做, 防冲突)** — 每批并行结束后, 主 agent **统一**:
   - 写共享文件(目录 README / 路由配置 / i18n locale / barrel `index.ts` / `package.json`)—— **绝不让多 agent 同时写**
   - 改这批任务的 `status` → `done`
   - 跑一次 lint + 类型检查兜底
   - 再进下一层
5. **失败隔离** — 某个并行 agent 失败 → 不影响同批其他;单独重试或标 `blocked`。

**何时直接串行**(别硬拆, 见 concurrency.md 第六节): 任务 < 3 个 / 文件高度重叠 / 需顺序推理 / 单条线性链。

### 任务状态机

```
pending → in-progress → done
                      ↘ blocked (遇到问题停下问用户)
```

- 开始一个任务: `status` 改为 `in-progress`
- 完成: 改为 `done`
- 卡住 (需用户决策): 改为 `blocked`, 在任务对象里加 `blockReason` 字段, 停下问用户

### 每个任务的实现步骤

对 tasks[] 里每个任务, 按以下步骤执行:

1. **读 prdRef 原文** — 按 `task.prdRef` (如 `docs/prds/login.md#账号密码登录`) 定位到 PRD 二级标题下全部内容, 理解业务上下文

2. **读设计稿（有 designRef 时必须执行）** — 如果 `task.designRef` 非空, 用 Read 工具加载图片：
   - 识别页面整体布局结构（顶部/中部/底部区域划分）
   - 提取可见的颜色、字体大小、间距、圆角等视觉规格
   - 列出页面包含的所有 UI 组件及其层级关系
   - 将识别结果作为实现的**视觉参考**, 优先级高于凭感觉猜测
   - `designRef` 为空时跳过此步

3. **查 Design Token（task.type 为 screen / page / component / widget 时必须执行）**：
   - 检查项目根目录是否存在 `docs/designs/DESIGN.md`；**不存在则跳过此步**
   - 存在时读取 DESIGN.md，提取本任务涉及的 token：
     - 颜色 → `colors.*`（通过 CSS 变量 / theme token 引用，禁止内联 hex）
     - 字体 → `typography.*`（通过 theme textStyle 引用，禁止内联 fontSize/fontWeight）
     - 间距 → `spacing.*`（通过 spacing 常量引用，禁止内联数字）
     - 圆角 → `rounded.*`（通过 radius 常量引用，禁止内联数字）
   - 确认项目已有 theme token 文件（如 `src/theme/`、`src/styles/tokens.ts`、`tailwind.config.ts` 等）；**文件不存在时停下**，提示先创建 theme token 任务再继续
   - task.type 为其他类型（model/api/store/util/constant/i18n/config）时跳过此步

4. **确认文件路径** — `task.filePath`, 目录不存在则创建

5. **写代码**, 必须遵守:
   - **文件头 JSDoc** 包含 `@description` / `@module` / `@dependencies` / `@prd` / `@task` / `@rules` / `@design` (参考 `.claude/rules/file-docs.md`)
   - **`@prd` 字段**: 直接用 `task.prdRef` 原值
   - **`@task` 字段**: `docs/tasks/<文件名>.json#<taskId>`
   - **`@rules` 字段**: 把 `task.businessRules` 每条按顺序列进去, **原文照抄, 不要改述**
   - **`@design` 字段**: 直接用 `task.designRef` 原值 (Figma 链接 / 本地文件路径), 无设计稿则省略
   - **API 类型**: `import type { paths } from '@/types/api'`, **不得手写** request/response 类型
   - **禁止硬编码**: 文案走 i18n, 颜色/尺寸走 theme token, 枚举走常量 (参考 `.claude/rules/no-hardcode.md`)
   - **组件**: 函数式 + Props interface 导出 + 业务逻辑抽 hooks

6. **维护目录 README.md** — 在文件所在目录的 README.md 文件清单加一行 (参考 `.claude/rules/file-docs.md`)
7. **完成后更新 status** — 把 `tasks.json` 对应任务的 `status` 从 `in-progress` 改为 `done`
8. **简短汇报** — 输出一句: 「✅ T00X 完成: <文件路径>」

### 什么时候停下问用户 (不要自作主张)

- PRD 规则模糊或互相矛盾
- OpenAPI 缺必要字段 (按 plan.md 规则, 加一条 blocked 任务推后端)
- 依赖的上游任务未完成
- 要选技术方案 (多种实现都合理时)
- 要新建未在 tasks[] 里的文件 (说明 `/plan` 漏拆了任务, 应回去补 plan)

### 什么时候不要停

- 样式细节 (颜色/间距) — 按 theme token 合理选
- 文件内部命名 — 按编码规范走
- JSDoc 措辞 — 按模板套

## 全部任务完成后

### 第一步: Visual QA (强制执行, 有设计截图时)

检查 `docs/designs/screenshots/reference/` 目录是否存在参考截图 (`.png` / `.jpg`)。

**有截图时**, 执行以下流程:

```bash
bash docs/designs/screenshots/run-visual-qa.sh
```

脚本会自动完成：截图（自动检测 dev server / 否则启动后截图关闭）→ 像素对比 → 生成差值图 → 输出 P0/P1/P2 报告。

完成后读取结果并做视觉确认：

```bash
cat docs/designs/screenshots/actual/qa-result.json
```

再用 Read 工具读取 `docs/designs/screenshots/actual/side-by-side.png` 做视觉判断。

**P0/P1 有差异时**（脚本退出码 = 2）：
- 读 `docs/designs/screenshots/actual/diff.png` 定位红色差异区域
- 找到对应 `.less` / `.module.css` / `.tsx` 文件，用 Edit 工具修复
- 重新执行脚本验证，最多尝试 3 轮
- 若差异根因是 `businessRules` 描述不精确 → 同步修 PRD 或 tasks.json，避免下次重蹈

**P2 差异**：记录在报告里，不阻塞继续。

**无截图时**: 跳过本步, 提示用户把设计截图放入 `docs/designs/screenshots/reference/` 以启用 Visual QA。

---

### 第二步: 汇总与提示

1. 汇总本次产出的文件清单
2. 提示下一步:
   ```
   ✅ 模块 login 全部任务完成 (共 N 个)

   建议下一步:
     1. 启动 dev 验证: pnpm dev
     2. 生成测试: /test workspace/src/features/login/
     3. 代码审查: /review workspace/src/features/login/
   ```
3. 如果任务清单里有留存的 `blocked` 任务, 一并列出提醒

## 输入

$ARGUMENTS

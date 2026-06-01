# docs 目录说明

本目录存放 AI 前端自动化工作流产生的所有文档。

## 目录结构

```
docs/
├── README.md              ← 你正在看的这个文件
├── WORKFLOW.md            ← 八步法工作流手册
├── PERMISSIONS.md         ← 权限弹窗与免打扰设置 (为什么弹/怎么配/人不在时远程接管)
├── ADAPTING.md            ← 跨工种适配清单 (后端/数据/移动/DevOps/... fork 本框架时读这个)
├── DECISIONS.md           ← 架构决策记录 (ADR), 框架重大决策的背景/理由
├── tasks/                 ← /plan 生成的任务清单
│   ├── tasks-user-module-2026-03-30.json
│   └── ...
├── prds/                  ← /prd 生成的产品需求文档
│   ├── _template.md
│   ├── REVIEW.md          ← PRD 人工审阅指南
│   └── login.md
├── bug-reports/           ← 测试端 AI 测试报告 (喂给 /fix 批量修)
│   ├── _template.md
│   ├── README.md          ← 测试端 AI 的 prompt 片段 + 对接说明
│   ├── 2026-04-16-login.md
│   └── screenshots/
├── test-reports/          ← /test 产出的单次测试报告快照 (不可变)
│   ├── README.md
│   ├── _template.md
│   └── 2026-05-19-1430-search-form.md
└── retrospectives/        ← /meta-audit 产出的只读观察报告 (不可变快照)
    ├── README.md
    └── 2026-04-20-meta-audit.md
```

## tasks/ 目录

存放由 `/plan` 命令生成的 JSON 任务清单。每个文件对应一个功能模块的开发任务拆解。

### 文件命名规则

```
tasks-[模块名英文]-[日期].json
```

### 文件内容说明

```json
{
  "moduleName": "模块名称",
  "summary": "模块功能概述",
  "createdAt": "生成日期",
  "tasks": [
    {
      "taskId": "T001", // 任务唯一标识
      "type": "api", // 类型: api | store | component | hook | page
      "name": "userApi", // 文件/模块名称
      "filePath": "workspace/src/...", // 目标文件路径
      "description": "...", // 具体实现要求
      "props": {}, // Props 接口定义 (组件才有)
      "dependencies": [], // 依赖的其他任务 taskId
      "reuseComponents": [], // 可复用的已有组件
      "acceptanceCriteria": [], // 验收标准
      "status": "pending" // 状态: pending | in-progress | done | blocked
    }
  ],
  "routeConfig": {}, // 路由配置
  "dataFlow": "..." // 数据流向说明
}
```

### status 状态说明

| 状态        | 含义                        |
| ----------- | --------------------------- |
| pending     | 待开发                      |
| in-progress | 开发中                      |
| done        | 已完成                      |
| blocked     | 被阻塞 (依赖未完成或有问题) |

### 怎么使用这些文件

```bash
# 编码时引用任务清单
> 请根据 @docs/tasks/tasks-user-module-2026-03-30.json 从 T001 开始实现

# 更新任务状态
> 把 @docs/tasks/tasks-user-module-2026-03-30.json 中 T001 的 status 改为 done

# 查看哪些任务还没完成
> 读取 @docs/tasks/tasks-user-module-2026-03-30.json，列出所有 status 不是 done 的任务
```

## prds/ 目录

存放产品需求文档, 是「需求 → 代码 → 测试」可追溯链的源头。
**所有源码 JSDoc 的 `@prd` 字段都引用这里的小标题作为锚点**, 所以小标题要稳定、清晰。

### 文件命名

```
docs/prds/<模块名英文>.md   例如 docs/prds/user-list.md
```

### 写作模板

参考 [docs/prds/_template.md](_template.md), 必含字段:
- 元信息 (模块代号、负责人、状态)
- 每个功能点用二级标题 (`## 搜索表单`), 标题即锚点
- **业务规则** 章节 (测试断言的来源, 必须可测试)
- 字段定义 / 异常场景

### 与 `/prd` `/plan` `/test` 的联动

```bash
# 0. 口语化需求 → PRD 草稿 (新)
/prd 我要做一个登录功能
# AI 会问 3-5 个关键问题, 然后生成草稿到 docs/prds/login.md
# 用户回头补齐 [待确认] 项

# 1. 已有结构化 PRD
docs/prds/user-list.md  (含 ## 搜索表单 锚点)

# 2. 拆任务 (plan 命令会自动写入 prdRef)
/plan @docs/prds/user-list.md

# 3. 编码 (源文件 JSDoc 写入 @prd / @task / @rules)
@prd docs/prds/user-list.md#搜索表单

# 4. 生成测试 (test 命令读 @prd 拉规则, 按规则生成 it())
/test workspace/src/features/list/components/SearchForm.tsx
```

### 锚点稳定性

⚠️ 重命名小标题 = 改 URL, 所有 `@prd` 引用都会失效。如必须改:
1. 全局搜索 `@prd .*#<旧标题>`
2. 同步更新源码 JSDoc
3. 提交时在 commit message 中标注「PRD 锚点变更」

## test-reports/ 目录

存放由 `/test` 命令产出的**单次测试报告快照**。每次执行 `/test` 都会在这里落一份新文件 — 无论本轮全绿、部分失败还是自动修复放弃。每份报告捕获:

- 执行汇总 (总用例 / 通过 / 失败 / 跳过 / 耗时)
- **业务规则追溯矩阵** — 每个源文件的 `@rules` ↔ `it()` ↔ 状态映射, 并附数值化的 `规则覆盖率: <已覆盖>/<总数>` 行 (本项目认可的真实覆盖指标, 参见 `.claude/rules/testing.md`)
- 本轮变更 (相比上一份报告新增/修改/删除的用例)
- 按类别分诊的未解决问题 (测试代码 / 环境 / 源码 bug) 和仍未覆盖的规则

### 命名

```
docs/test-reports/<YYYY-MM-DD-HHmm>-<范围>.md
```

`<范围>` 为 kebab-case: 文件基名 (`search-form`)、模块名 (`features-list`), 或全项目 `all`。

### 不可变性

与 `retrospectives/` 同理, 这里的报告**只追加, 不修改** — 历史报告永不编辑, 让趋势从时间序文件列表里自然浮现。完整约定见 [test-reports/README.md](test-reports/README.md), 骨架见 [test-reports/_template.md](test-reports/_template.md)。

### 与 bug-reports/ 的关系

| 来源 | 捕获内容 | 流向 |
|------|----------|------|
| `bug-reports/` | 人 / E2E AI 在运行态发现的用户可见缺陷 | `/fix` 批量修复 |
| `test-reports/` (本目录) | `/test` 跑出的单测/组件测试覆盖率与失败 | 代码评审 / 回顾 |

两者互补, 不互相替代。

## retrospectives/ 目录

`/meta-audit` 命令产出的**只读观察报告**, 记录某一时刻框架的健康度快照 (规则违规 / 文档漂移 / 追溯链断裂 / 死引用等)。

- **不可变**: 报告一旦生成不再修改, 下次审计基于当前状态生成新报告, 自然对比趋势
- **不自动执行**: 所有改动需人工 review 后走正常 PR 流程固化, 不要在报告里打勾「已处理」
- **命名**: `<YYYY-MM-DD>-meta-audit.md`

详见 [retrospectives/README.md](retrospectives/README.md)。

## PERMISSIONS.md

**权限弹窗与免打扰设置**。解决"人离开电脑、流程被 Yes/No 确认框卡死"的高频痛点。讲清:

- **为什么会弹** —— 弹窗的两个来源(AI 自己问 vs harness 权限框),以及为什么"默认 yes"对后者无效
- **怎么配** —— 权限模式分级(`acceptEdits` / `auto` / `bypassPermissions`)、命令白名单写法、本框架已配的默认值
- **人不在时远程接管** —— Claude App 推送 / Remote Control / IM Notification Hook 三通道对比与配法

## DECISIONS.md

架构决策记录 (ADR), 记录框架**重大设计决策**的背景、理由、替代方案。未来接手的 AI / 新人读这里就能快速理解「为什么这么做」, 避免误改或重走弯路。

什么该记录、什么不该记录、格式模板见文件顶部。

## ADAPTING.md

**跨工种适配清单**。本框架虽然针对前端, 但 80% 机制是领域无关的。如果你想把这套骨架搬到后端 / 数据 / 移动 / DevOps / QA / 设计 / 产品 / 写作 / 科研 等工种, 从这里入手:

- 哪些**直接照搬** (内核层: 八步法骨架 / 可追溯链 / 硬性闸门 / ADR)
- 哪些**保留结构换内容** (领域层: `.claude/rules/*` 五个规则文件)
- 哪些**整块替换** (工种特化层: `workspace/` 工作区)
- 八步法 × 9 工种映射表 + 八步迁移清单

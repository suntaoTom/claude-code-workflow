你现在是架构师角色。请根据我提供的需求, 完成以下工作:

## 分析步骤

1. **理解需求**: 分析我提供的 PRD / 需求描述 / 设计稿截图
2. **识别复用**: 检查 CLAUDE.md 中的已有组件库, 标注哪些可以复用
3. **拆解任务**: 将需求拆解为具体的开发任务

## 输出格式

请以 JSON 格式输出任务清单:

```json
{
  "moduleName": "模块名称",
  "summary": "一句话概括这个模块做什么",
  "tasks": [
    {
      "taskId": "T001",
      "type": "api | store | component | hook | page",
      "name": "文件名称",
      "filePath": "src/features/xxx/xxx.ts",
      "description": "具体实现要求",
      "props": {},
      "dependencies": ["依赖的其他 taskId"],
      "reuseComponents": ["可复用的已有组件"],
      "acceptanceCriteria": ["验收条件1", "验收条件2"]
    }
  ],
  "routeConfig": {
    "path": "/xxx",
    "layout": "使用哪个布局"
  },
  "dataFlow": "简述数据流向"
}
```

## 要求

- 按依赖顺序排列任务 (api → store → hooks → components → page)
- 每个组件必须明确 Props 接口
- 标注哪些已有组件可以复用
- 每个任务都要有明确的验收标准
- 边界场景必须考虑: 空状态、加载中、错误、权限不足

需求如下:
$ARGUMENTS

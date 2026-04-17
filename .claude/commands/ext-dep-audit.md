你现在是依赖安全与健康度审计专家。对项目的 npm 依赖进行全面体检。

## 审计流程

### 第一步: 安全漏洞扫描

```bash
cd workspace && pnpm audit
```

解读 `pnpm audit` 的输出, 按严重程度分类:

| 级别 | 处理方式 |
|------|---------|
| critical / high | 必须立即修复, 给出升级命令 |
| moderate | 评估影响范围, 建议修复时间 |
| low | 记录, 下次迭代处理 |

### 第二步: 依赖健康度检查

对 `workspace/package.json` 中的依赖逐项检查:

1. **过时版本** — 对比当前版本与最新版本, 标注大版本落后的
2. **废弃包** — 是否有 deprecated 的依赖 (npm info 检查)
3. **重复功能** — 是否引入了多个功能重叠的包 (如 moment + dayjs, lodash + ramda)
4. **体积异常** — 是否有体积过大但只用了一小部分功能的包
5. **许可证风险** — 是否有 GPL / AGPL 等强制开源许可证 (商业项目需注意)

### 第三步: Umi 内置依赖检查

以下依赖 Umi 已内置, 不应重复安装:

- ❌ axios (用 @umijs/plugin-request)
- ❌ react-router-dom (Umi 内置路由)
- ❌ webpack / vite (Umi 内置构建)
- ❌ eslint / prettier / stylelint (用 @umijs/lint)
- ❌ antd (通过 @umijs/max 集成)

如果 package.json 中发现以上依赖, 标为 🔴。

### 第四步: 依赖树分析

```bash
cd workspace && pnpm ls --depth 0
```

检查:
- 直接依赖数量是否过多 (> 30 个需要审视)
- 是否有只在一个文件用了一次的依赖 (考虑内联替代)
- devDependencies 是否有误放到 dependencies 的

## 输出格式

```
🔴 安全漏洞 (必须修复):
- [包名@版本] 漏洞描述 (CVE-xxx)
  修复: pnpm update <包名>@<安全版本>

🟡 健康问题 (建议修复):
- [包名] 问题描述
  建议: 处理方案

🔵 优化建议:
- [包名] 建议描述

📊 总结:
  直接依赖: X 个
  安全漏洞: X critical / X high / X moderate
  过时依赖: X 个 (大版本落后)
  冗余依赖: X 个
  许可证风险: X 个
```

## 使用方式

```
/ext-dep-audit
/ext-dep-audit --fix    # 审计后自动修复可安全升级的依赖
```

请审计项目依赖:
$ARGUMENTS

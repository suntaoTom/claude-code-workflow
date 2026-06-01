# 权限弹窗与免打扰设置

> 解决一个高频痛点:人离开电脑去忙别的事,Claude Code 跑到一半弹出 "Allow this?" / "Yes or No" 确认框,整个流程卡死干等。
> 本文说明 **为什么会弹窗**、**怎么配置减少弹窗**、以及 **人不在时如何远程接管** 那些真正需要决策的弹窗。

---

## 一、为什么会出现这些弹窗?——两个完全不同的来源

很多人以为"告诉 AI 默认 yes"就能不弹,但说了还是弹。原因是弹窗其实来自**两个不同的地方**,解法也不同:

| 来源 | 谁在问 | 例子 | 归谁管 |
|------|--------|------|--------|
| **① AI 在对话里问你** | Claude 自己 | "要继续吗?""这样改对吗?" | CLAUDE.md / `.claude/rules/` / memory |
| **② harness 权限框** | Claude Code 外壳层 | "Allow this bash command?"(改文件/跑命令前的确认) | **只能靠 `settings.json` 权限配置** |

> ⚠️ **关键认知**:来源 ② 的弹窗,**你在 CLAUDE.md 或 memory 里写一万遍"默认 yes"都没用** —— 弹框时根本轮不到 AI 说话,是外壳在拦。它**只能**通过权限配置(白名单 / 权限模式)解决。

### 来源 ② 最常卡人的形态:复合 bash 一行流

即使 `cat` / `grep` / `ls` 各自都在白名单里,一条这样的命令仍会整体弹框:

```bash
cd /path; echo "==="; cat package.json | grep "scripts"; ls; head -40 README.md
```

因为带 `;` / `&&` / `cd` 的**复合命令**,外壳按整体判断,匹配不上单命令前缀白名单。
**对策**:查看文件 / 搜索时优先用 Read / Grep / Glob 专用工具(永不弹框),少把多步塞进一条 bash。

---

## 二、怎么配置减少弹窗

### 2.1 权限模式(Permission Mode)分级

按 `Shift+Tab` 可在会话内切换;在 `settings` 里设 `permissions.defaultMode` 可设为默认。

| 模式 | 行为 | 适合 |
|------|------|------|
| `default`(Ask before edits) | 每次改文件 / 跑命令都问 | 谨慎 / 新手 |
| `acceptEdits`(Edit automatically) | **改文件**自动放行;**bash 命令仍按白名单逐条判** | 平衡 |
| `auto`(Auto mode) | 分类器判断:安全可逆的(只读 bash、改文件)**自动放行**,危险的(删库/force push/发布)才拦 | **人不在时最佳** |
| `bypassPermissions` | 全自动,什么都不弹(危险动作也放过) | 风险全担 |

> 📌 **重点**:`acceptEdits` 只自动放行**改文件**,你那条 `cat/grep` 的 **bash 还是会弹**(除非命中白名单)。
> 如果目标是"人不在时安全的事别问我",**`auto`(Auto mode)比 `acceptEdits` 更贴** —— 它连只读 bash 也自动放行,只拦真正危险的。

### 2.2 命令白名单(allow)

`settings.json` / `settings.local.json` 的 `permissions.allow` 里加**命令前缀**,命中的不再弹:

```jsonc
{
  "permissions": {
    "allow": [
      "Read", "Edit", "Write", "Glob", "Grep",     // 工具级:整类放行
      "Bash(git:*)",                                 // git 全子命令
      "Bash(cat:*)", "Bash(head:*)", "Bash(tail:*)", // 只读查看
      "Bash(grep:*)", "Bash(rg:*)", "Bash(find:*)",  // 搜索
      "Bash(wc:*)", "Bash(sort:*)", "Bash(uniq:*)",
      "Bash(diff:*)", "Bash(tree:*)", "Bash(sed:*)"
    ],
    "deny": [
      "Bash(rm -rf:*)"                               // 底线:危险命令永远拦
    ],
    "defaultMode": "acceptEdits"
  }
}
```

**前缀语法**:
- `"Bash(git:*)"` → 匹配 `git` 开头的所有命令
- `"Bash(pwd)"` → 精确匹配单条
- `"Read"` → 整个工具放行

**写白名单的原则**:写**通用前缀**(`Bash(grep:*)`),不要写**完整命令字符串**(`Bash(grep -l "X" src/...)`)—— 后者换个参数就不匹配,等于没加。

### 2.3 本框架已配的默认值

`.claude/settings.local.json` 已设:
- `defaultMode: acceptEdits`
- `allow` 补了只读命令前缀:`head/tail/grep/rg/find/wc/sed/sort/uniq/diff/tree`(`cat/ls/git:*` 原有)
- 保留 `deny: Bash(rm -rf:*)` 底线

> 注:`settings.local.json` 虽列在 `.gitignore`,但本仓库它**已被 git 跟踪**(先 commit 后加 ignore,gitignore 只对未跟踪文件生效),所以这份默认值会随仓库带给 fork 出去的新项目。若想让默认值更"官方"(强制带给所有克隆者),可把**只读白名单部分**挪到已提交的 `.claude/settings.json`;但 `defaultMode` 属个人风险偏好,建议留在 local。

---

## 三、人不在电脑前 → 远程接管那些必须决策的弹窗

即便配了 Auto mode,真正不可逆 / 对外的动作(删库、force push、发版、链上交易)仍会停下等你 —— 这正是远程方案的价值:手机收到提醒,远程点确认。

Claude Code 原生支持,有两条可叠加的通道:

| 通道 | 设置项 / 机制 | 能做什么 | 账号要求 |
|------|--------------|----------|----------|
| **Claude App 推送** | `inputNeededNotifEnabled`(等你决策时推送)/ `agentPushNotifEnabled`(主动推送) | 收到后**直接点 Yes/No 操作** | **必须同账号** + 装 App |
| **Remote Control** | `remoteControlAtStartup` / `claude.ai/code` | 会话镜像到 claude.ai,手机上看到弹窗并接管 | **必须同账号** |
| **IM 推送**(飞书/钉钉/企微/TG/Bark) | **Notification Hook** → webhook | **只通知**,免账号,能进任意群 | **无账号要求,可推给任何人/群** |

### 两条通道的本质区别

- **"通知"可以无账号、推给任何人**(用 Notification Hook 打 webhook)
- **"远程点按钮"必须同账号、用官方 App / claude.ai**(驱动你自己的机器,安全所限)
- 二者可**同时触发**:同一个弹窗,IM 群里先戳你"有事等你",再打开 Claude App 点确认。一个叫醒你,一个让你动手。

### Notification Hook 推到 IM 的配法(示例:webhook)

webhook URL 是密钥,放 **`settings.local.json`(本地不入库)**,不要提交。以**飞书自定义机器人**为例(已实测可用):

```jsonc
{
  "hooks": {
    "Notification": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "msg=$(jq -r '.message // \"有操作在等你处理\"'); curl -s -X POST \"<飞书webhook>\" -H 'Content-Type: application/json' -d \"$(jq -nc --arg t \"🔔 Claude Code 提醒: $msg\" '{msg_type:\"text\",content:{text:$t}}')\" >/dev/null 2>&1 || true",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

**原理**:`Notification` 事件触发时,harness 把 `{"message":"..."}` 从 stdin 喂给命令 → `jq` 抠出 `.message` → 再用 `jq -nc` 包成飞书要求的 `{msg_type:"text",content:{text:...}}` → `curl` POST 给 webhook。

**注意各家 IM 的 payload 格式不同**:
- **飞书**:`{"msg_type":"text","content":{"text":"..."}}`(上例)
- 企微/钉钉:`{"msgtype":"text","text":{"content":"..."}}`
- Bark/ntfy:直接 GET/POST 纯文本到设备 URL
- 飞书若开了「自定义关键词」安全设置,消息文字里必须含该关键词(上例含 "Claude")

### ⚠️ 隐私提醒

Remote Control 会把会话**镜像到 claude.ai 云端**(手机才够得着),即会话内容经 Anthropic 服务器中转。涉及敏感代码的项目需知悉此事实再决定开启。Notification Hook 只外发一行提醒文本,不上传会话。

---

## 四、配套的 AI 行为约定(来源 ① 的解法)

权限配置只管来源 ②。来源 ①(AI 自己问)由规则 / memory 约束,原则是:

> **可逆的事默认推进,不问;只有不可逆 / 对外发布(force push、删库、发版、部署、链上交易)才停下来攒着,等用户回来一次性确认。**

详见 `.claude/rules/` 与各项目 memory。两者缺一不可:**配置管"外壳弹的",规则管"AI 问的"**。

---
name: add-card-trigger
description: 使用语音/口述内容在工作区 `fleeting/` 文件夹下创建 Obsidian 风格的快速笔记；需要默认 `fleeting` 标签与 1-2 句概括时触发，可调用脚本自动生成 Markdown。
metadata:
  author: flash-hu
  version: "0.1"
---

# Add Card Trigger

## 概览

将口述内容即时整理为 Obsidian 笔记：存于仓库根目录 `fleeting/`，文件名即标题，frontmatter 自带 `fleeting` 标签，正文只有 1-2 句概述，便于后续加工至永久笔记。

## 快速流程

1. **确认输入**：获取标题与口述文本，必要时补充来源/下一步。  
2. **提炼概述**：提取触发点 + 洞察/行动，只保留 1-2 句陈述句，避免项目符号。  
3. **生成 Markdown**：套用模板并写入 `fleeting/<Title>.md`（不存在则新建目录）。  
4. **反馈路径**：返回文件位置及概述，方便用户校对。

### Markdown 模板

```markdown
---
tags:
  - fleeting
---

<1-2 句概述>
```

## 快速脚本：`create_note.py`

- 路径：`skills/add-card-trigger/scripts/create_note.py`
- 功能：自动创建目录、写入模板、保持 `tags` frontmatter。
- 参数：`--title`（必填，仅用于文件名）、`--summary`（概述）、`--folder`（默认 `fleeting`）、`--tags`（默认只含 `fleeting`，可多值）。

### 示例

```bash
python skills/add-card-trigger/scripts/create_note.py \
  --title "回顾AI白板想法" \
  --summary "需要把白板协同点子整理成 Miro 流程，并在下周前验证能否嵌入 Roadmap。"
```

执行后会显示 `Created note at <path>` 以供复制。

## 注意事项

- 概述保持 40-60 字以内，优先描述“洞察/行动 + 价值”。  
- 如口述含行动项，使用 “动词 + 结果” 句式（例如“准备 demo，验证可行性”）。  
- 遇到包含非法字符的标题需与用户确认替换写法，可在摘要开头保留原文，文件名使用兼容版本。  
- 若脚本不可用，可按模板手动创建；务必确认 Obsidian 同步目录最新。

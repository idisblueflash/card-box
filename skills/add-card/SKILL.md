name: add-card
description: 当用户已经具备标题/摘要（来自口述整理或其他技能的引用提炼）时，触发此技能将内容写入仓库 `fleeting/` 目录，生成带默认 `fleeting` 标签、1-2 句概述的 Obsidian 快速笔记。
metadata:
  author: flash-hu
  version: "0.1"
---

# Add Card

## 概览

将口述内容即时整理为 Obsidian 笔记：存于仓库根目录 `fleeting/`，文件名即标题，frontmatter 自带 `fleeting` 标签，正文只有 1-2 句概述，便于后续加工至永久笔记。

## 输入场景

1. **确认输入**：获取标题与口述文本。  
2. **提炼概述**：只保留 1-2 句概括语，避免项目符号。  
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

- 路径：`skills/add-card/scripts/create_note.py`
- 功能：自动创建目录、写入模板、保持 `tags` frontmatter。
- 参数：`--title`（必填，仅用于文件名）、`--summary`（概述）、`--folder`（默认 `fleeting`）、`--tags`（默认只含 `fleeting`，可多值）。

### 示例

```bash
python skills/add-card/scripts/create_note.py \
  --title "回顾AI白板想法" \
  --summary "需要把白板协同点子整理成 Miro 流程，并在下周前验证能否嵌入 Roadmap。"
```

执行后会显示 `Created note at <path>` 以供复制。

## 注意事项

- 概述保持 40-60 字以内，优先描述“洞察/行动 + 价值”。  
- 遇到包含非法字符的标题，脚本会自动去除.

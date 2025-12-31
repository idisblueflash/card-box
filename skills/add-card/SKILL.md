---
name: add-card
description: 当用户已经具备标题/摘要（来自口述整理或其他技能的引用提炼）时，触发此技能将内容写入仓库 `fleeting/` 目录，生成带默认 `fleeting` 标签、1-2 句概述的 Obsidian 快速笔记。
metadata:
  author: flash-hu
---

# Add Card

## 概览

将用户口述或其他技能传入的原始文本转化为 Obsidian 闪念卡：先在本技能内完成关键词提取、标题命名与摘要压缩，再通过脚本把结果写入 `fleeting/`（可通过参数覆盖）。  
👉 上游技能（如 quote-card-trigger）只需负责判断是否需要写卡，并把原文传给 `add-card`；本技能内部承担“关键信息抽取 + 调脚本写入”两件事。

## 输入场景

1. **接收原文**：从调用方获取原始口述、引用内容或自由文本，可附带期望标签。  
2. **抽取关键信息**：在技能中完成标题命名、1-2 句摘要与标签决策（默认 `fleeting`）。摘要应在复述用户原话的基础上做“轻度压缩”，不得引入新场景、新指标或未被用户提及的推断；用户原句里的情绪词或语境词（如“反思”“复盘”“提醒”等）若无特殊说明必须保留。  
3. **执行脚本**：调用 `create_note.py`，把生成的 `title`、`summary`、`tags` 等参数传入，脚本负责目录创建、文件名清理与 Markdown 写入。  
4. **返回结果**：脚本输出 `Created note at <path>`，并追加一个 ```card_json fenced block，包含 `title`（实际标题）、`tags`（标签数组）、`summary`（1-2 句摘要），供 Evaluation 解析。

### Markdown 模板

```markdown
---
tags:
  - fleeting
---

<1-2 句概述>
```

## 调用方式：`create_note.py`

- 路径：`skills/add-card/scripts/create_note.py`
- 功能：根据抽取好的字段（标题、摘要、标签、目录）写入 Markdown，保持 frontmatter 结构。
- 参数：
  - `--title`：必填，用于文件名和 frontmatter；脚本会自动去除非法字符。
  - `--summary`：必填，1-2 句概述。
  - `--folder`：可选，默认 `fleeting`。
  - `--tags`：可选，多值；若未提供则自动使用 `fleeting`。

### 示例

```bash
python skills/add-card/scripts/create_note.py \
  --title "回顾AI白板想法" \
  --summary "需要把白板协同点子整理成 Miro 流程，并在下周前验证能否嵌入 Roadmap。"
```

执行后会显示 `Created note at <path>` 以及一个 `card_json` fenced block，可在后续 Evaluation 中解析 `title / tags / summary`。

## 注意事项

- **忠实压缩**：摘要必须 100% 建立在用户输入的原意之上，只允许合并句子、删除重复或语气词；不得补充测试步骤、时间节点、行动计划等新增内容，更不得添加“以保障…”“为了…”等目的性语句。若用户强调“反思/复盘/提醒”等语义，请保留这些关键词或等价短语。  
- **不要推理动机**：总结时只复述发生的事实或待办，禁止猜测原因、成果或价值说明；除非原文已有表述，否则不要写“确保…”“降低风险”等推断。  
- **引用式表达**：优先沿用用户的词语或短短的“同义换句话说”，避免改写成完全不同的描述；不必陈述文件路径或技能名。  

- 调用方只需判断是否触发写卡；原文在 `add-card` 内部完成抽取与压缩。  
- 概述保持 40-60 字以内，优先描述“洞察/行动 + 价值”。  
- 遇到包含非法字符的标题，脚本会自动去除；若清洗后为空，文件名将回退为 `Untitled`。  
- `tags` 为空时自动补上 `fleeting`，传入 `literature` / `permanent` 等标签将按原值写入。

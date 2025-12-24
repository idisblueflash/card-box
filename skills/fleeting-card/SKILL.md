---
name: fleeting-card
description: 使用语音/口述内容在工作区 `fleeting/` 文件夹下创建 Obsidian 风格的快速笔记；需要默认 `fleeting` 标签与 1-2 句概括时触发，可调用脚本自动生成 Markdown。
---

# Fleeting Part

## 概览

将用户口述的零散想法整理成符合 Obsidian 规范的 markdown 笔记，统一写入仓库根目录下的 `fleeting/` 文件夹。每条笔记使用标题作为文件名、默认挂载 `fleeting` 标签，并输出 1-2 句高度概括的描述，方便后续整理。

## 工作流程

1. **收集输入**  
   - 向用户确认笔记标题（若未提供，可根据主题生成简洁标题）。  
   - 记录原始口述内容，并澄清是否需要附加上下文或来源。

2. **提炼概述（1-2 句）**  
   - 识别关键信息（触发点、洞察、下一步想法）。  
   - 合并重复信息，避免使用长段落或项目符号。  
   - 语气偏陈述式：“想法/观察 + 可能行动/价值”。

3. **准备文件内容**  
   使用以下模板（`<...>` 需替换）：

   ```markdown
   ---
   title: <Title>
   created: <ISO 时间戳>
   tags:
     - fleeting
   ---

   # <Title>

   <1-2 句概括>
   ```

4. **创建/覆盖文件**  
   - 目标目录：仓库根目录下的 `fleeting/`。若目录缺失，需先创建。  
   - 文件名：与标题完全一致（末尾自动添加 `.md`）。如标题包含非法文件字符，需与用户确认替代写法。  
   - 可以调用脚本自动化，也可手动创建。

5. **回显**  
   - 返回生成文件的路径及概述内容，方便用户快速确认。

## 快速脚本：`create_fleeting_note.py`

路径：`skills/fleeting-card/scripts/create_fleeting_note.py`

### 用途
- 自动确保 `fleeting/` 目录存在并写入符合模板的 markdown。
- 生成 frontmatter（title、created、tags）以及正文标题/摘要。

### 调用示例

```bash
python skills/fleeting-card/scripts/create_fleeting_note.py \
  --title "回顾AI白板想法" \
  --summary "需要把白板上的 AI 协同点子整理成Miro流程，并在下周前验证是否能嵌入当前Roadmap。" \
  --folder fleeting \
  --tags fleeting
```

> 备注：`--tags` 默认为 `fleeting`，如需附加标签可输入多个值（例如 `--tags fleeting idea reference`）。

### 参数说明
- `--title`：必填，亦作为文件名。  
- `--summary`：口述内容的 1-2 句概括。  
- `--folder`：可选，默认 `fleeting`。允许将笔记写到 Obsidian 保险箱中的其他相对路径。  
- `--tags`：可选列表，脚本会写入 frontmatter。

脚本执行后会输出 `Created note at <path>` 以便复制。

## 关键注意事项

- 概述须足够短（理想 40-60 个字），突出价值或下一步，而非逐字稿。  
- 如果口述包含行动项，使用 “动词 + 成果” 结构（如“准备 demo，验证 XX 是否可行”）。  
- 任何非 ASCII 的标题在生成文件名前需确认系统是否支持；必要时保留原文作为 `title`，同时提供兼容版本的文件名。  
- 若脚本不可用，可手动创建文件，但需保持上述模板与标签一致。  
- 确保最终笔记与 Obsidian 同步目录一致，必要时提醒用户刷新/重新索引。

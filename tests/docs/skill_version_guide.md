# Skill 独立版本指南（SemVer + Changelog）

> 目标：每个 Skill 都有自己的版本号；用户本地可见；任何改动都能追溯到 ChangeLog；AI agent 能据此自动 bump 版本并写日志。

## 1. 版本放在哪里（单一事实来源）
每个 Skill 的版本号必须写在该 Skill 的 `SKILL.md` YAML frontmatter 里：

```yaml
---
name: add-card
description: 把语音/文本整理成 Obsidian Fleeting Note，并写入指定目录。
metadata:
  package: card-box
  version: "0.4.2"
  released: "2025-12-31"
  changelog: "CHANGELOG.md#add-card"
  source: "https://github.com/idisblueflash/card-box"
---
```

规则
	•	metadata.version 是唯一权威（不要在 README 里再写一份版本号，避免不一致）。
	•	released 建议写（方便用户本地判断是否过时）。
	•	changelog 指向总 CHANGELOG.md 的锚点（或本 skill 的 changelog）。

## 2. SemVer 语义（MAJOR.MINOR.PATCH）

对每个 Skill 单独使用 SemVer。

PATCH（修复/不改变行为的增强）

满足任意一条就 bump patch：
	•	修 bug（输出错误、路径错误、边界条件崩）
	•	输出内容更稳定，但不改变字段含义/结构
	•	日志、提示、注释、性能优化（不影响结果）

示例：0.4.1 -> 0.4.2

MINOR（新增能力且向后兼容）

满足任意一条就 bump minor：
	•	新增可选参数/配置（旧用法仍可跑）
	•	新增输出字段（旧字段不变；消费者不需要改也能继续用）
	•	扩展支持的输入类型（旧输入仍 OK）

示例：0.4.2 -> 0.5.0

MAJOR（破坏兼容）

满足任意一条就 bump major：
	•	删除/重命名已有参数
	•	修改输出结构/字段含义，导致依赖方需要改
	•	默认行为改变且影响用户已有流程（比如输出目录、文件名规则、frontmatter 结构变更）

示例：0.5.3 -> 1.0.0

## 3. 什么算一次版本变化
	•	一次 PR/一次发布里，一个 Skill 最多 bump 一次版本。
	•	如果一个 PR 同时改了多个 Skill，就分别 bump 各自版本（互不影响）。

## 4. ChangeLog 书写规范

仓库根目录维护一个 CHANGELOG.md（推荐单文件分区）。

结构模板

```md
# Changelog

## add-card
### 0.4.2 - 2025-12-31
- Fix: 处理空输入时不再生成空文件
- Perf: 减少重复写盘

### 0.5.0 - 2026-01-02
- Feat: 支持可选参数 `tags` 覆盖默认值
- Docs: 补充示例

## split-note
### 0.2.0 - 2025-12-20
- Feat: 支持按标题分段
```

日志分类（建议固定词）
	•	Feat: 新增能力（通常 MINOR）
	•	Fix: 修复 bug（通常 PATCH）
	•	Break: 破坏性改动（必须 MAJOR，并写迁移说明）
	•	Perf: 性能优化（通常 PATCH）
	•	Docs: 文档变化（如果不影响行为，可不 bump；或 PATCH）

迁移说明（MAJOR 必须写）

当出现 Break: 时，在该条目下增加：
	•	What changed
	•	How to migrate
	•	Before/After 示例（尽量短）

## 5. AI agent 自动更新规则（操作顺序）

当 AI agent 修改了某个 Skill（代码或提示词或模板）时，必须按顺序做：
	1.	判断变更类型：Patch / Minor / Major
	2.	计算新版本号
	3.	更新该 Skill 的 SKILL.md：
	•	metadata.version
	•	metadata.released（用当天日期）
	4.	更新 CHANGELOG.md：
	•	在对应 Skill 分区顶部新增一段 ### <new_version> - <date>
	•	写清楚用户可感知的变化（不要写“refactor/clean up”这种对用户无意义的句子）

## 6. 常见判定例子（给 AI 更好用）
	•	只改了提示词让输出更短更清晰，但结构没变 → PATCH
	•	新增 frontmatter 字段 tags，旧流程不需要改 → MINOR
	•	把输出字段 title 改名 note_title → MAJOR
	•	默认输出目录从 Fleeting/ 改到 Inbox/ → MAJOR
	•	修复 Windows 路径分隔符问题 → PATCH

## 7. 可选：提供一个 info skill

建议加一个 card-box-info skill：
	•	扫描所有 skills/*/SKILL.md
	•	输出：skill name + version + released + changelog anchor
	•	用于用户在本地快速确认已安装版本
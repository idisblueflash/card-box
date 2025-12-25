# Agent 指南（card-box）

## 本地 Skill 构建要点

1. **技能目录**：当前核心技能为 `skills/add-card` 与 `skills/quote-card-trigger`；新增技能沿用相同结构（`SKILL.md` + `scripts/`），并在此文件中登记调用方式。
2. **工作目录**：默认脚本均在仓库根目录执行，路径引用使用相对仓库根的写法（例如 `tests/fixtures/...`）。
3. **触发验证流程**：先用 Codex CLI（`scripts/run_codex_exec.py` 或 `scripts/run_codex_batch.py`）生成日志，再用 DeepEval 验证技能是否在日志中触发。

## 脚本与测试运行方式

### 单次 Codex 运行（`scripts/run_codex_exec.py`）

```bash
python3 scripts/run_codex_exec.py --text "what is 2+2?"
```

- 附加 Codex 参数使用 `--codex-arg`（可重复）；
- `--output-file out.json` 同时写入结果文件；
- 默认 `--timeout 60`，可根据需要调大；
- `--working-dir` 控制执行目录（默认 `.`）。

### 批量运行（`scripts/run_codex_batch.py`）

```bash
python3 scripts/run_codex_batch.py \
  --input-file tests/fixtures/quote_card_trigger_cases.jsonl \
  --output-dir tests/fixtures \
  --parallel 2 \
  --timeout 120
```

- 若 JSONL 中包含 `log_file` 字段，输出写入该相对路径（相对 JSONL 所在目录）；
- 支持 `--max-cases`（仅跑部分数据）和 `--overwrite`（重新生成既有文件）。

### DeepEval（仅 CLI）

```bash
uv run deepeval test run tests/deepeval/test_skill.py
```

- 依赖 `tests/fixtures/codex_run*.json`；确认该文件由 `run_codex_exec.py` 生成；
- 不使用 pytest 包装 DeepEval。

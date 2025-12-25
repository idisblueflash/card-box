# card-box

## 开发

### 测试 `scripts/run_codex_exec.py`

该脚本用于包装 `codex exec --json`，输入 prompt、追加原生命令参数，并输出结构化 JSON。基本测试方式如下：

```bash
python3 scripts/run_codex_exec.py --text "what is 2+2?"
```

示例输出包含事件列表与返回文本（例如 `2+2 equals 4.`）。若需附加 Codex 参数（如切换模型），可重复传递 `--codex-arg`：

```bash
python3 scripts/run_codex_exec.py \
  --text "explain this in one sentence" \
  --codex-arg "--model gpt-4o-mini"
```

脚本非零退出码表示 Codex 执行失败，可根据 JSON 中的 `exit_code`、`stderr` 分析原因。如需把结果保存为文件，可追加 `--output-file out.json`，脚本会在标准输出的同时写入该文件。默认会等待 Codex 最多 60 秒，可使用 `--timeout 120` 这样的参数调整上限，避免长时间 prompt 被过早中断。

### Skill 触发测试（tests/deepeval/test_skill_trigger.py）

`tests/deepeval/test_skill_trigger.py` 会读取 `output/codex_run.json` 作为 Codex 执行日志，验证纯引用块输入是否触发 `quote-card-trigger` 技能。运行前请先用 `scripts/run_codex_exec.py` 生成该 JSON（例如把示例引用作为输入，并使用 `--output-file output/codex_run.json` 保存）。然后运行：

```bash
pytest tests/deepeval/test_skill_trigger.py
```

由于测试只消费现有 JSON，不会直接调用模型，但生成 fixture 的 `run_codex_exec.py` 步骤依旧需要本地 Codex CLI 与网络。

### DeepEval 测试

如果想通过 DeepEval CLI 复用相同的断言，可运行：

```bash
uv run deepeval test run tests/deepeval/test_skill.py
```

同样需要事先准备 `output/codex_run.json`；该测试会确保日志中包含对 `quote-card-trigger` 技能的调用。

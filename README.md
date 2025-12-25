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

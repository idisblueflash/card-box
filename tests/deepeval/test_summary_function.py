from __future__ import annotations

import sys
from pathlib import Path

from deepeval import evaluate
from deepeval.metrics import SummarizationMetric
from deepeval.test_case import LLMTestCase

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tests.deepeval.summary_harness import run_summary_agent  # noqa: E402


SUMMARY_PROMPTS = [
    "[$add-card](/Users/husongtao/.codex/skills/add-card/SKILL.md) 今天复盘账会要完成登录功能的买点验证。",
    "[$add-card](/Users/husongtao/.codex/skills/add-card/SKILL.md) 今天有一些反思,需要记录一下。 比如说需要提前准备演示的环境。 这里面应该可以向研发申请额外的测试机器。",
]


def test_summary_agent_prompts():
    metric = SummarizationMetric()
    test_cases = []

    for prompt in SUMMARY_PROMPTS:
        tool_name, tool_args = run_summary_agent(prompt, focus_task="summary", strict_no_extra_output=True)
        assert tool_name == "post_summary", "Summary agent did not invoke the expected tool."

        actual_summary = (tool_args or {}).get("content", "")
        assert actual_summary, "Summary agent returned empty content."

        test_cases.append(
            LLMTestCase(
                input=prompt,
                actual_output=actual_summary,
            )
        )

    evaluate(test_cases=test_cases, metrics=[metric])

from __future__ import annotations

import json
from pathlib import Path
from typing import Literal, Any
from openai import OpenAI


client = OpenAI()


REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_PATH = REPO_ROOT / "skills" / "add-card" / "SKILL.md"
tools = [
    {
        "type": "function",
        "name": "post_summary",
        "description": "Post the generated summary text to an external harness for testing.",
        "parameters": {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "Summary string emitted by the add-card prompt.",
                },
            },
            "required": ["content"],
        },
    }
]


def load_add_card_skill() -> str:
    """Return the contents of skills/add-card/SKILL.md."""
    if not SKILL_PATH.exists():
        raise FileNotFoundError(f"Missing add-card skill definition: {SKILL_PATH}")
    return SKILL_PATH.read_text(encoding="utf-8")



FocusTask = Literal["summary", "title", "tags"]

def build_system_prompt(
    focus_task: FocusTask,
    required_tool_name: str,
    strict_no_extra_output: bool = False,
) -> str:
    """
    Build a Chinese system prompt for test override mode.

    Args:
        focus_task: "summary" | "title" | "tags"
        required_tool_name: tool/function name the model must call exactly once.
        strict_no_extra_output: if True, add a rule to forbid any extra text output
                               besides the tool call (useful when tool_choice is forced).

    Returns:
        The system prompt string.
    """
    if not required_tool_name or not required_tool_name.strip():
        raise ValueError("required_tool_name must be a non-empty string")

    focus_task = focus_task.strip()
    required_tool_name = required_tool_name.strip()

    lines = [
        "你现在处于【测试覆盖模式】。本次测试的唯一目标是：验证你是否会按要求调用指定的工具，并且不执行与本次测试目标无关的任何步骤。",
        "",
        "总规则（最高优先级）：",
        f"1) 只允许执行本次指定的测试目标：{focus_task}（可选值：summary / title / tags）。",
        f"2) 必须且只能调用一次工具：{required_tool_name}。",
        "3) 严禁调用、提及或模拟任何写文件/落盘行为；严禁提及或执行 create_note.py；严禁输出 “Created note at …” 等任何文件相关内容。",
        "4) 除了完成第 2 条的工具调用之外，不要进行额外的工具调用或多步流程（例如：不要生成标题+摘要+标签的全流程，不要组装完整卡片，不要做多轮自我修正）。",
        "5) 如果你无法调用指定工具，请输出：ERROR: TOOL_CALL_REQUIRED",
    ]

    if strict_no_extra_output:
        lines.insert(
            6,
            "附加规则：除工具调用外，不要输出任何文本内容（包括解释、总结、示例或多余标点）。",
        )

    return "\n".join(lines)





def build_input_messages(user_text: str, focus_task: FocusTask, strict_no_extra_output: bool = False) -> list[dict]:
    """Construct conversation messages with system/developer/user roles."""
    system_prompt = build_system_prompt(
        focus_task,
        required_tool_name="post_summary",
        strict_no_extra_output=strict_no_extra_output,
    )
    return [
        {"role": "system", "content": system_prompt},
        {"role": "developer", "content": load_add_card_skill()},
        {"role": "user", "content": user_text},
    ]

def _ensure_dict(obj: Any) -> dict:
    if isinstance(obj, dict):
        return obj
    if hasattr(obj, "model_dump"):
        try:
            return obj.model_dump()
        except Exception:
            pass
    if hasattr(obj, "__dict__"):
        return dict(obj.__dict__)
    return {}


def extract_target_parameters(response_obj: Any, target_tool: str = "post_summary") -> tuple[str, dict]:
    """Extract the tool call name and arguments from a Responses API result."""
    payload = _ensure_dict(response_obj)
    outputs = payload.get("output")
    if outputs is None and hasattr(response_obj, "output"):
        outputs = response_obj.output
    if outputs is None:
        raise ValueError("Response payload does not contain 'output' entries.")

    for output in outputs:
        output_dict = _ensure_dict(output)
        output_type = output_dict.get("type")
        if output_type in {"tool_call", "function_call"}:
            name = output_dict.get("name")
            arguments = output_dict.get("arguments")
            if isinstance(arguments, str):
                try:
                    arguments = json.loads(arguments)
                except json.JSONDecodeError:
                    arguments = {"raw": arguments}
            if name == target_tool:
                return name or "", arguments or {}

        contents = output_dict.get("content")
        if not contents:
            continue
        for content in contents:
            content_dict = _ensure_dict(content)
            if content_dict.get("type") not in {"tool_call", "function_call"}:
                continue
            call = content_dict.get("tool_call") or content_dict
            name = call.get("name")
            arguments = call.get("arguments")
            if isinstance(arguments, str):
                try:
                    arguments = json.loads(arguments)
                except json.JSONDecodeError:
                    arguments = {"raw": arguments}
            if name == target_tool:
                return name, arguments or {}
    raise ValueError(f"No tool call named '{target_tool}' found in response.")

def run_summary_agent(user_text: str, focus_task: FocusTask = "summary", strict_no_extra_output: bool = True) -> tuple[str | None, dict | None]:
    """High-level wrapper to run the summary harness and extract tool call arguments."""
    input_messages = build_input_messages(
        user_text=user_text,
        focus_task=focus_task,
        strict_no_extra_output=strict_no_extra_output,
    )
    response = client.responses.create(
        model="gpt-5-mini",
        tools=tools,
        input=input_messages,
        tool_choice={"type": "function", "name": "post_summary"},
    )
    try:
        tool_name, tool_args = extract_target_parameters(response)
    except ValueError:
        return None, None
    return tool_name, tool_args


if __name__ == "__main__":
    tool_name, tool_args = run_summary_agent(
        "[$add-card](/Users/husongtao/.codex/skills/add-card/SKILL.md) 今天复盘账会要完成登录功能的买点验证。"
    )
    print(f"Tool name: {tool_name}")
    print(f"Arguments: {tool_args}")

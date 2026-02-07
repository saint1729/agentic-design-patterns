"""Starter scaffold for the Tool Use pattern.

This example shows how to structure a loop where the model decides to call
an external tool (simulated here) and then uses the tool output to produce
a final answer. The tool is mocked so the script is runnable without keys.
Replace `mock_tool_call` with real tool invocations (search API, calculator,
or custom service) as needed.
"""
import asyncio
import json
from typing import Dict, Any

from dotenv import load_dotenv


load_dotenv()


async def mock_tool_call(tool_name: str, input_data: str) -> Dict[str, Any]:
    """Simulate external tool behavior.

    Supported mock tools:
    - `web_search`: returns fake search hits
    - `calculator`: evaluates simple arithmetic expressions (very limited)
    """
    await asyncio.sleep(0.1)
    if tool_name == "web_search":
        return {
            "results": [
                {"title": "Result A", "snippet": f"Found about {input_data}."},
                {"title": "Result B", "snippet": f"More on {input_data}."},
            ]
        }
    if tool_name == "calculator":
        try:
            # WARNING: eval used only for the toy mock; do NOT use eval on untrusted input.
            value = eval(input_data, {"__builtins__": {}})
            return {"value": value}
        except Exception as e:
            return {"error": str(e)}
    return {"error": "unknown tool"}


def model_decides_tool(prompt: str) -> Dict[str, str]:
    """Simple decision function: which tool to call, and what input to send.

    Replace with an LLM call that outputs a JSON decision in real usage.
    """
    if "calculate" in prompt.lower():
        return {"tool": "calculator", "input": "2 + 2 * 3"}
    return {"tool": "web_search", "input": prompt}


async def tool_use_pipeline(user_prompt: str) -> str:
    decision = model_decides_tool(user_prompt)
    print("Decision:", decision)
    tool_out = await mock_tool_call(decision["tool"], decision["input"])
    print("Tool output:", json.dumps(tool_out, indent=2))
    # Simple synthesis step combining prompt + tool output
    if decision["tool"] == "calculator" and "value" in tool_out:
        return f"Answer (calculator): {tool_out['value']}"
    if decision["tool"] == "web_search" and "results" in tool_out:
        summaries = ", ".join(r["snippet"] for r in tool_out["results"])[:200]
        return f"Answer (search-based): {summaries}"
    return "Could not produce an answer"


async def main():
    prompts = [
        "Who won the world series in 2020?",
        "Please calculate 2+2*3 for me.",
    ]
    for p in prompts:
        print("\nPrompt:", p)
        out = await tool_use_pipeline(p)
        print("Final answer:", out)


if __name__ == "__main__":
    asyncio.run(main())

"""Starter example for the Reflection pattern.

This is a small, runnable scaffold that demonstrates a local "reflection" loop
without requiring an active LLM API key. Replace the `mock_llm_call` with
real LLM calls (LangChain/OpenAI) when you're ready.
"""
import asyncio
import os
from typing import Tuple

from dotenv import load_dotenv


load_dotenv()


async def mock_llm_call(prompt: str) -> str:
    """Simulated LLM response to keep the example runnable offline.

    This returns a predictable transformation so users can iterate locally.
    """
    await asyncio.sleep(0.1)
    return f"[LLM RESPONSE to: {prompt}]"


def evaluate_response(resp: str) -> Tuple[bool, str]:
    """Simple reflection heuristic: return (is_good, feedback).

    This is a placeholder for more sophisticated critique or scoring logic.
    """
    if "TODO" in resp or resp.strip() == "":
        return False, "Response incomplete or placeholder detected"
    if len(resp) < 20:
        return False, "Response too short"
    return True, "Looks good"


async def reflection_loop(initial_prompt: str, max_rounds: int = 3) -> str:
    prompt = initial_prompt
    for round_idx in range(1, max_rounds + 1):
        print(f"Round {round_idx}: sending prompt ->", prompt)
        resp = await mock_llm_call(prompt)
        print("Model output:", resp)
        ok, feedback = evaluate_response(resp)
        print("Reflection feedback:", feedback)
        if ok:
            return resp
        # simple refine step: incorporate feedback into next prompt
        prompt = f"{initial_prompt}\n
Please improve the previous response: {feedback}"
    return resp


async def main():
    example_prompt = "Summarize the Reflection design pattern in one paragraph."
    final = await reflection_loop(example_prompt, max_rounds=3)
    print("Final output:\n", final)


if __name__ == "__main__":
    asyncio.run(main())

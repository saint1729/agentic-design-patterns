"""
ADK Generator–Critic–Refiner Loop (with terminal condition) using LoopAgent

What you get:
- DraftWriter: produces an initial draft once (stored in state["draft_text"])
- Critic: reviews the draft and either:
    - outputs EXACT completion phrase (meaning “done”), OR
    - outputs actionable critique (stored in state["critique"])
- Refiner: if done -> calls exit_loop() to terminate the LoopAgent
          else -> applies critique and overwrites state["draft_text"]
- LoopAgent: runs [Critic, Refiner] repeatedly up to max_iterations or until exit_loop() escalates.

How to run:
1) pip install python-dotenv google-adk google-genai   (package names may vary in your env)
2) .env in same folder:
      GOOGLE_API_KEY=...
      GOOGLE_MODEL_ID=gemini-2.0-flash
3) python adk_loop_reflection.py
"""

import asyncio
import os
import uuid

from dotenv import load_dotenv

from google.adk.agents import LoopAgent, LlmAgent, SequentialAgent
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.tools.tool_context import ToolContext
from google.genai.types import Content, Part

# ----------------------------
# Configuration
# ----------------------------
load_dotenv()

MODEL_ID = os.getenv("GOOGLE_MODEL_ID")
if not os.getenv("GOOGLE_API_KEY"):
    raise RuntimeError("Missing GOOGLE_API_KEY. Put it in .env or export it.")

APP_NAME = "adk_loop_reflection_demo"
USER_ID = "saint1729"

# State keys
STATE_DRAFT = "draft_text"
STATE_CRITIQUE = "review_output"

# Terminal condition phrase (Critic must output EXACTLY this when draft is good)
COMPLETION_PHRASE = "No major issues found."


# ----------------------------
# Tool: exit loop
# ----------------------------
def exit_loop(tool_context: ToolContext):
    """
    Call this ONLY when the Critic indicates completion.
    Setting `tool_context.actions.escalate = True` tells ADK to stop the loop.
    """
    print(f"[Tool Call] exit_loop() triggered by agent={tool_context.agent_name}")
    tool_context.actions.escalate = True
    tool_context.actions.skip_summarization = True
    return {}  # Tools should return JSON-serializable output


# ----------------------------
# 1) Initial Generator (runs once)
# ----------------------------
draft_writer = LlmAgent(
    name="DraftWriter",
    model=MODEL_ID,
    include_contents="none",
    description="Generates the initial draft content on a given subject.",
    instruction="""
You are a concise technical writer.
Write a short, informative paragraph about the user's subject (3–5 sentences).
Do not use headings or bullet points.
Output ONLY the paragraph text.
""".strip(),
    output_key=STATE_DRAFT,
)

# ----------------------------
# 2a) Critic (runs inside the loop)
# ----------------------------
critic = LlmAgent(
    name="Critic",
    model=MODEL_ID,
    include_contents="none",
    description="Reviews the draft and either approves it or provides actionable critique.",
    instruction=f"""
You are a meticulous reviewer.

Draft to review:
{{{STATE_DRAFT}}}


Completion criteria:
1) The paragraph is coherent and informative for the given subject.
2) No obvious factual errors or overconfident claims.
3) No fluff; clear and concise writing.

Task:
- If ALL criteria are met, respond EXACTLY with: "{COMPLETION_PHRASE}"
- Otherwise, respond with a concise bullet list of specific improvements.

Output ONLY your critique text (or the exact completion phrase).
""".strip(),
    output_key=STATE_CRITIQUE,
)

# ----------------------------
# 2b) Stopping tool agent (runs inside the loop, checks for completion)
# ----------------------------
stopper = LlmAgent(
    name="Stopper",
    model=MODEL_ID,
    include_contents="none",
    tools=[exit_loop],
    description="Stops the loop when the critic approves.",
    instruction=f"""
Critique:
{{{STATE_CRITIQUE}}}

Rule:
- If the critique is EXACTLY "{COMPLETION_PHRASE}", call `exit_loop()`.
- Otherwise, output ONLY the single word: CONTINUE.
""".strip(),
    # IMPORTANT: no output_key here (so it can't overwrite draft_text)
)

# ----------------------------
# 2c) Refiner (runs inside the loop)
# ----------------------------
refiner = LlmAgent(
    name="Refiner",
    model=MODEL_ID,
    include_contents="none",
    description="Refines the draft based on critique, or exits the loop if complete.",
    tools=[exit_loop],
    instruction=f"""
You refine drafts.

Current draft:
{{{STATE_DRAFT}}}

Critique:
{{{STATE_CRITIQUE}}}

Apply the critique and output ONLY the refined paragraph (3–5 sentences).
""".strip(),
    # Overwrite the draft in state on each refinement iteration
    output_key=STATE_DRAFT,
)

# ----------------------------
# 3) LoopAgent: Critic -> Refiner until exit_loop or max_iterations
# ----------------------------
reflection_loop = LoopAgent(
    name="DraftReviewLoop",
    sub_agents=[critic, stopper, refiner],  # order matters: critique first, then stop, then refine/exit
    max_iterations=5,
)

# ----------------------------
# 4) Full pipeline: initial draft once, then loop until done
# ----------------------------
root_agent = SequentialAgent(
    name="WriteReviewRefinePipeline",
    sub_agents=[draft_writer, reflection_loop],
    description="Writes an initial draft, then iteratively critiques/refines until acceptable.",
)


# ----------------------------
# Runnable entrypoint
# ----------------------------
async def run_once(subject: str):
    session_service = InMemorySessionService()
    runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)

    session_id = f"session_{uuid.uuid4().hex[:8]}"
    await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=session_id)

    # The user's message becomes “the subject” the DraftWriter writes about.
    new_message = Content(role="user", parts=[Part(text=subject)])

    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session_id,
        new_message=new_message,
    ):
        # Uncomment to see event stream:
        # print(event)
        pass

    # Inspect final state
    session = await session_service.get_session(app_name=APP_NAME, user_id=USER_ID, session_id=session_id)
    state = session.state or {}

    return {
        "final_draft": state.get(STATE_DRAFT, ""),
        "last_critique": state.get(STATE_CRITIQUE, ""),
    }


def main():
    subject = "The James Webb Space Telescope (JWST)"
    result = asyncio.run(run_once(subject))

    print("\n========== FINAL DRAFT ==========\n")
    print(result["final_draft"])

    print("\n========== LAST CRITIQUE ==========\n")
    print(result["last_critique"])


if __name__ == "__main__":
    main()

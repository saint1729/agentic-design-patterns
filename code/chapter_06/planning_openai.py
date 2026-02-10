import os

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file for security

# ----------------------------
# Initialize the client
# ----------------------------
# Replace with your API key OR rely on OPENAI_API_KEY env var
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ----------------------------
# System + User messages
# ----------------------------
system_message = """
You are a professional researcher preparing a structured, data-driven report.
Focus on data-rich insights, use reliable sources, and include inline citations.
"""

user_query = "Research the economic impact of semaglutide on global healthcare systems."

MODEL_ID = os.getenv("OPENAI_DR_MODEL_NAME")

# ----------------------------
# Deep Research API call
# ----------------------------
response = client.responses.create(
    model=MODEL_ID,
    input=[
        {
            "role": "developer",
            "content": [
                {
                    "type": "input_text",
                    "text": system_message
                }
            ],
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": user_query
                }
            ],
        },
    ],
    reasoning={"summary": "auto"},
    tools=[{"type": "web_search_preview"}],
)

# ----------------------------
# Final report text
# ----------------------------
final_report = response.output[-1].content[0].text
print(final_report)

# ----------------------------
# Access inline citations
# ----------------------------
print("\n--- CITATIONS ---")
annotations = response.output[-1].content[0].annotations

if not annotations:
    print("No annotations found in the report.")
else:
    for i, citation in enumerate(annotations):
        cited_text = final_report[citation.start_index:citation.end_index]
        print(f"Citation {i + 1}:")
        print(f"  Cited Text: {cited_text}")
        print(f"  Title: {citation.title}")
        print(f"  URL: {citation.url}")
        print(f"  Location: chars {citation.start_index}-{citation.end_index}")
        print()

print("\n" + "=" * 50 + "\n")

# ----------------------------
# Inspect intermediate steps
# ----------------------------
print("--- INTERMEDIATE STEPS ---")

# 1. Reasoning steps (summaries only)
try:
    reasoning_step = next(
        item for item in response.output if item.type == "reasoning"
    )
    print("\n[Found a Reasoning Step]")
    for summary_part in reasoning_step.summary:
        print(f"- {summary_part.text}")
except StopIteration:
    print("\nNo reasoning steps found.")

# 2. Web search calls
try:
    search_step = next(
        item for item in response.output if item.type == "web_search_call"
    )
    print("\n[Found a Web Search Call]")
    print(f"  Query Executed: '{search_step.action['query']}'")
    print(f"  Status: {search_step.status}")
except StopIteration:
    print("\nNo web search steps found.")

# 3. Code execution steps (if any)
try:
    code_step = next(
        item for item in response.output if item.type == "code_interpreter_call"
    )
    print("\n[Found a Code Execution Step]")
    print("  Code Input:")
    print(f"```python\n{code_step.input}\n```")
    print("  Code Output:")
    print(code_step.output)
except StopIteration:
    print("\nNo code execution steps found.")

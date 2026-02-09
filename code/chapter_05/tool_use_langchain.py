import os
import asyncio
import nest_asyncio
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool as langchain_tool
from langchain.agents import create_agent

load_dotenv()

MODEL_ID = os.getenv("GOOGLE_MODEL_ID")

llm = ChatGoogleGenerativeAI(model=MODEL_ID, temperature=0)


@langchain_tool
def search_information(query: str) -> str:
    """
    Provides factual information on a given topic (simulated).
    """
    print(f"\n--- 🛠️ Tool Called: search_information with query: '{query}' ---")

    simulated_results = {
        "weather in london": "The weather in London is currently cloudy with a temperature of 15°C.",
        "capital of france": "The capital of France is Paris.",
        "population of earth": "The estimated population of Earth is around 8 billion people.",
        "tallest mountain": "Mount Everest is the tallest mountain above sea level.",
        "default": (
            f"Simulated search result for '{query}': No specific information found, "
            "but the topic seems interesting."
        ),
    }

    result = simulated_results.get(query.lower(), simulated_results["default"])
    print(f"--- TOOL RESULT: {result} ---")
    return result


tools = [search_information]

# New-style agent (LangChain v1)
agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="You are a helpful assistant. Use tools when needed.",
)

async def run_agent(query: str):
    print(f"\n--- 🏃 Running Agent with Query: '{query}' ---")

    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": query}]}
    )

    messages = result.get("messages", [])
    if not messages:
        print("\n🛑 No messages returned.")
        print(result)
        return

    last = messages[-1]
    print("\n--- ✅ Final Agent Response ---")
    if hasattr(last, "content"):
        print(last.content)
    else:
        print(last.get("content", ""))

async def main():
    await asyncio.gather(
        run_agent("What is the capital of France?"),
        run_agent("What's the weather like in London?"),
        run_agent("Tell me something about dogs."),
    )

nest_asyncio.apply()
asyncio.run(main())

import os
import uuid
from typing import Dict, Any, Optional

from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.adk.tools import FunctionTool
from google.genai import types
from google.adk.events import Event

from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file


MODEL_ID = os.getenv("MODEL_ID")

def booking_handler(request: str) -> str:
    """Simulates the Booking Agent handling a request."""
    print("\n--- DELEGATING TO BOOKING HANDLER ---")
    return f"Booking Handler processed request: '{request}'. Result: Simulated booking action."

def info_handler(request: str) -> str:
    """Simulates the Info Agent handling a request."""
    print("\n--- DELEGATING TO INFO HANDLER ---")
    return f"Info Handler processed request: '{request}'. Result: Simulated information retrieval."

def unclear_handler(request: str) -> str:
    """Handles unclear requests."""
    print("\n--- HANLDING UNCLEAR REQUEST ---")
    return f"Coordinator could not delegate request: '{request}'. Please clarify."

booking_tool = FunctionTool(booking_handler)
info_tool = FunctionTool(info_handler)

booking_agent = Agent(
    name="Booker",
    model=MODEL_ID,
    description="A specialized agent that handles all flight and hotel booking requests by calling the booking tool.",
    tools=[booking_tool],
)

info_agent = Agent(
    name="Info",
    model=MODEL_ID,
    description="A specialized agent that handles general information and answers user questions by calling the info tool.",
    tools=[info_tool],
)

coordinator = Agent(
    name="Coordinator",
    model=MODEL_ID,
    instruction=(
        "You are the main coordinator. Your only task is to analze incoming user requests"
        " and delegate them to the appropriate specialist agent. Do not try to answer the user directly.\n"
        "- For any request related to booking flights or hotels, delegate to the 'Booker' agent.\n"
        "- For all other general information questions, delegate to the 'Info' agent.\n"
    ),
    description="A coordinator agent that routes user requests to the correct specialist agent.",
    # The presence of sub_agents enables LLM-driven delegation (Auto-Flow) by default.
    sub_agents=[booking_agent, info_agent],
)

# --- Execution Logic ---

async def run_coordinator(runner: InMemoryRunner, request: str) -> str:
    """Runs the coordinator agent with the given user request and delegates."""
    print(f"\n--- Running coordinator with request: '{request}' ---")
    final_result = ""
    try:
        user_id = "user_123"
        session_id = str(uuid.uuid4())
        await runner.session_service.create_session(
            app_name=runner.app_name,
            user_id=user_id,
            session_id=session_id,
        )

        for event in runner.run(
            user_id=user_id,
            session_id=session_id,
            new_message=types.Content(
                role='user',
                parts=[types.Part(text=request)]
            )
        ):
            if event.is_final_response() and event.content:
                # Try to get text directly from event.content to avoid iterating parts
                if hasattr(event.content, 'text') and event.content.text:
                    final_result = event.content.text
                elif event.content.parts:
                    ## Fallback: Iterate through parts and extract text (might trigger warning)
                    text_parts = [part.text for part in event.content.parts if part.text]
                    final_result = "".join(text_parts)
                # Asumming the loop should break after the final response
                break

        print(f"Coordinator Final Response: {final_result}")
        return final_result
    except Exception as e:
        print(f"An error occurred while processing your request: {e}")
        return f"An error occurred while processing your request: {e}"

async def main():
    """Main function to run the ADK example."""
    print("--- Google ASK Routing Example (ADK Auto-Flow Style) ---")
    print("Note: This requires Google ADK installed and authenticated.")

    runner = InMemoryRunner(coordinator)
    # Example Usage
    result_a = await run_coordinator(runner, "Book me a hotel in Paris.")
    print(f"Final Output A: {result_a}")
    result_b = await run_coordinator(runner, "What is the highest mountain in the world?")
    print(f"Final Output B: {result_b}")
    result_c = await run_coordinator(runner, "Tell me a random fact.")
    print(f"Final Output C: {result_c}")
    result_d = await run_coordinator(runner, "Find flights to Tokyo next month.") # Should go to Booker
    print(f"Final Output D: {result_d}")


if __name__ == "__main__":
    import asyncio

    # Run the async main entrypoint
    asyncio.run(main())

# scripts/run_milo_chat.py
import os
import asyncio
import logging
from dotenv import load_dotenv

from autogen_agentchat.ui import Console
from autogen_core import CancellationToken
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient

# Import the function to create Milo
from milo_agent.agent import create_milo_agent

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    # Load environment variables from .env file
    load_dotenv()

    # --- LLM Configuration ---
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("OPENAI_API_KEY not found in .env file or environment variables.")
        print("Error: OPENAI_API_KEY is required. Please set it in your .env file.")
        return

    # Configure the OpenAI client
    # Use gpt-4o or another capable model that handles function/tool calling well
    model_client = OpenAIChatCompletionClient(model="gpt-4o", api_key=api_key)
    logger.info("OpenAI client configured.")

    # --- Agent Creation ---
    # Create Milo
    milo = create_milo_agent(model_client)
    logger.info("Agent '%s' created.", milo.name)

    # --- Start Chat ---
    print("\n--- Starting Chat with Milo ---")
    print("Enter your requests for Milo below.")
    print("Type 'exit' or 'quit' when you want to end the conversation.")
    print("-" * 30)

    await Console(
        milo.on_messages_stream(
            [
                TextMessage(
                    content="Hi Milo, can you tell me what you can do?", source="user"
                )
            ],
            cancellation_token=CancellationToken(),
        ),
        output_stats=True,  # Enable stats printing.
    )

    # Cleanup the client connection
    await model_client.close()
    logger.info("Chat finished and client closed.")
    print("-" * 30)
    print("--- Chat Ended ---")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nChat interrupted by user.")

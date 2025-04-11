"""
Milo is a personal and developer assistant.
"""

import asyncio
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken
from dotenv import load_dotenv
from agents.milo import milo
from utils.mcp import print_tools
from utils.console import rich_console
import logging

logging.basicConfig(level=logging.INFO)


async def main():
    """Main entry point for Milo."""

    logger = logging.getLogger(__name__)
    agent = await milo()

    print_tools(agent._tools)

    await rich_console(
        stream=agent.on_messages_stream(
            [
                TextMessage(
                    content="You have been activated. Greet the user.",
                    source="system",
                )
            ],
            cancellation_token=CancellationToken(),
        ),
        show_intermediate=True,
    )

    while True:
        try:
            user_input = input("> ")

            if user_input == "exit":
                logger.info("Session ended")
                break

            await rich_console(
                stream=agent.on_messages_stream(
                    [TextMessage(content=user_input, source="user")],
                    cancellation_token=CancellationToken(),
                ),
                show_intermediate=True,
            )
        except KeyboardInterrupt:
            logger.info("Session ended")
            break
        except EOFError:
            logger.info("Session ended")
            break


if __name__ == "__main__":
    load_dotenv()
    asyncio.run(main())

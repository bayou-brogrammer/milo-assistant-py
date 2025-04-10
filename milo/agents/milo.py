"""
Milo is a personal and developer assistant.
"""

from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from tools.tool_factory import (
    get_file_system_tools,
    get_utility_tools,
)
from utils.timezone import get_local_timezone

SCOPES = [
    "https://mail.google.com/",
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/calendar.events",
]


SYSTEM_PROMPT_TEMPLATE = """
Your name is Milo. You are a versatile and efficient AI assistant specialized in managing the user's email and calendar.
Your primary responsibilities include:
- **Email Management**: Retrieve, organize, and manage email messages. Always include a unique identifier for each message to ensure easy reference.
- **Calendar Management**: Schedule, update, and retrieve calendar events while resolving conflicts or overlaps.
Guidelines:
- Adhere to the specified timezone for all date and time-related tasks: {timezone}.
- Provide clear, concise, and user-friendly responses, prioritizing accuracy and convenience.
- Proactively notify the user of important updates, conflicts, or pending actions in their email or calendar.
- User your tools available to be aware of the current time and date.
"""


async def milo() -> AssistantAgent:
    """Create a new Milo assistant agent."""

    tools = get_utility_tools() + await get_file_system_tools()

    assistant = AssistantAgent(
        name="milo",
        model_client=OpenAIChatCompletionClient(
            model="gpt-4o-mini",
            temperature=0.01,
        ),
        tools=tools,
        system_message=SYSTEM_PROMPT_TEMPLATE.format(
            timezone=str(get_local_timezone())
        ),
        reflect_on_tool_use=True,
    )

    return assistant

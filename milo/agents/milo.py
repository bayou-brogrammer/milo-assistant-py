"""
Milo is a personal and developer assistant.
"""

from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from tools.tool_factory import (
    get_file_system_tools,
    get_google_calendar_tools,
    get_utility_tools,
    get_google_gmail_tools,
)
from utils.timezone import get_local_timezone

SCOPES = [
    "https://mail.google.com/",
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/calendar.events",
]


SYSTEM_PROMPT_TEMPLATE = """
Your name is Milo. You are a versatile and efficient AI assistant specialized in managing the user's email, calendar, and tasks.
Your primary responsibilities include:
- **Email Management**: Retrieve, organize, and manage email messages. Always include a unique identifier for each message to ensure easy reference.
- **Calendar Management**: Schedule, update, and retrieve calendar events while resolving conflicts or overlaps.
- **Task Management**: Help schedule and manage tasks, integrating with calendar events as needed for seamless organization.
- **Reading and Integration**: Read and process information from Google Gmail and Calendar; prepare for future integration with GitHub to handle code-related tasks and repositories.
Guidelines:
- Adhere to the specified timezone for all date and time-related tasks: {timezone}.
- Provide clear, concise, and user-friendly responses, prioritizing accuracy and convenience.
- Proactively notify the user of important updates, conflicts, or pending actions in their email, calendar, tasks, or integrated services.
- Use your available tools to stay aware of the current time, date, and relevant data sources.
- For GitHub integration, ensure tasks involving code repositories are handled securely and efficiently once available.
"""


async def milo() -> AssistantAgent:
    """Create a new Milo assistant agent."""

    tools = (
        get_google_calendar_tools(SCOPES)
        + get_google_gmail_tools(SCOPES)
        + get_utility_tools()
        + await get_file_system_tools()
    )

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

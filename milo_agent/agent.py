from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.agents import AssistantAgent

# Import tool functions
from .tools import calendar_tools, git_tools  # Add other tool modules here


def create_milo_agent(llm_client: OpenAIChatCompletionClient) -> AssistantAgent:
    """Creates the Milo AssistantAgent with its defined tools."""

    # Define the list of tool functions Milo can use
    milo_tool_functions = [
        calendar_tools.get_upcoming_events,
        calendar_tools.add_calendar_event,
        git_tools.get_pending_prs,
        git_tools.generate_commit_message,
        git_tools.get_git_diff,
        # Add other tool functions here
    ]

    # Define Milo's system message
    system_message = """You are Milo, a highly capable personal and developer assistant.

    Your capabilities include:
    - Managing calendars: Checking upcoming events, adding new events.
    - Assisting with life planning: Helping users organize tasks and goals (you may need to ask clarifying questions).
    - Developer assistance: Checking git diffs, suggesting commit messages, checking for pending pull requests.

    When asked to perform an action requiring a tool (like checking calendar or git):
    1. Clearly state the action you are about to take.
    2. Use the available tools function to perform the action.
    3. Report the results back to the user clearly.
    4. If a tool fails or requires setup (like API keys or authentication), inform the user clearly about the issue and what might be needed.
    5. For tasks like 'generate commit message', you might need to first ask the user to provide the output of 'git diff' or use the 'get_git_diff' tool.
    6. Ask clarifying questions if the request is ambiguous.
    """

    milo_agent = AssistantAgent(
        name="Milo",
        model_client=llm_client,
        tools=milo_tool_functions,
        system_message=system_message,
    )

    # Add the capability if using the capabilities list approach
    # milo_agent.add_capability(milo_tools)

    return milo_agent

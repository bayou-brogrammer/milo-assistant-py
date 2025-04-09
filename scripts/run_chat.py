"""
this is a simple example of how to use the AutoGen framework to create a chat application
"""

import asyncio
import os

import pandas as pd
from autogen_core.models import UserMessage
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.teams import RoundRobinGroupChat, SelectorGroupChat
from autogen_agentchat.ui import Console
from autogen_core import CancellationToken
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.tools.langchain import LangChainToolAdapter
from autogen_ext.tools.mcp import StdioServerParams, mcp_server_tools
from dotenv import load_dotenv
from langchain_experimental.tools.python.tool import PythonAstREPLTool

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
# Check if the required environment variable is set
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY not found in .env file or environment variables.")

gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file or environment variables.")

openai_model_client = OpenAIChatCompletionClient(
    model="gpt-4o-mini",
    api_key=openai_api_key,
)

gemini_model_client = OpenAIChatCompletionClient(
    model="gemini-2.0-flash",
    api_key=gemini_api_key,
)


async def simple_user_agent(model_client: OpenAIChatCompletionClient):
    """
    A simple example of a user agent that sends a message to the model client
    and prints the response.
    """
    response = await model_client.create(
        [UserMessage(content="What is the capital of France?", source="user")]
    )
    print(response)
    await model_client.close()


async def assistant_run(model_client: OpenAIChatCompletionClient) -> None:
    # Define a tool that searches the web for information.
    async def web_search(query: str) -> str:
        """Find information on the web"""
        return (
            "AutoGen is a programming framework for building multi-agent applications."
        )

    agent = AssistantAgent(
        name="assistant",
        model_client=model_client,
        tools=[web_search],
        system_message="Use tools to solve tasks.",
    )

    response = await agent.on_messages(
        [TextMessage(content="Find information on AutoGen", source="user")],
        cancellation_token=CancellationToken(),
    )
    print(response.inner_messages)
    print(response.chat_message)


async def mcp_agent(agent_name: str, model_client: OpenAIChatCompletionClient):
    # Get the fetch tool from mcp-server-fetch.
    fetch_mcp_server = StdioServerParams(command="uvx", args=["mcp-server-fetch"])
    tools = await mcp_server_tools(fetch_mcp_server)

    # Create an agent that can use the fetch tool.
    agent = AssistantAgent(
        name=agent_name,
        model_client=model_client,
        tools=tools,
        reflect_on_tool_use=True,
    )  # type: ignore

    # Let the agent fetch the content of a URL and summarize it.
    result = await agent.run(
        task="Summarize the content of https://en.wikipedia.org/wiki/Seattle"
    )
    assert isinstance(result.messages[-1], TextMessage)
    print(result.messages[-1].content)

    # Close the connection to the model client.
    await model_client.close()


async def longchain_agent():
    df = pd.read_csv(
        "https://raw.githubusercontent.com/pandas-dev/pandas/main/doc/data/titanic.csv"
    )
    tool = LangChainToolAdapter(PythonAstREPLTool(locals={"df": df}))
    print(tool.return_value_as_string(df))

    model_client = OpenAIChatCompletionClient(model="gpt-4o-mini")
    agent = AssistantAgent(
        "assistant",
        tools=[tool],
        model_client=model_client,
        system_message="Use the `df` variable to access the dataset.",
    )

    await Console(
        agent.on_messages_stream(
            [
                TextMessage(
                    content="What's the average age of the passengers?", source="user"
                )
            ],
            CancellationToken(),
        ),
        output_stats=True,
    )

    await model_client.close()


async def round_robin_team():
    # Create an OpenAI model client.
    model_client = OpenAIChatCompletionClient(
        model="gpt-4o-2024-08-06",
    )

    # Create the primary agent.
    primary_agent = AssistantAgent(
        "primary",
        model_client=model_client,
        system_message="You are a helpful AI assistant.",
    )

    # Create the critic agent.
    critic_agent = AssistantAgent(
        "critic",
        model_client=model_client,
        system_message="Provide constructive feedback. Respond with 'APPROVE' to when your feedbacks are addressed.",
    )

    # Define a termination condition that stops the task if the critic approves.
    text_termination = TextMentionTermination("APPROVE")

    # Create a team with the primary and critic agents.
    team = RoundRobinGroupChat(
        [primary_agent, critic_agent], termination_condition=text_termination
    )

    # When running inside a script, use a async main function and call it from `asyncio.run(...)`.
    await team.reset()  # Reset the team for a new task.
    await Console(team.run_stream(task="Write a short poem about the fall season."))


async def selector_team():
    """
    Demonstrates a multi-agent travel booking system using a SelectorGroupChat.

    This function creates a team of specialized travel agents:
    - Travel_Advisor: Coordinates the overall trip planning
    - Hotel_Agent: Provides hotel booking information for specified locations
    - Flight_Agent: Provides flight booking information between destinations

    The agents collaborate through a SelectorGroupChat, which intelligently selects
    the most appropriate agent to respond to each part of the travel booking process.
    The chat terminates when any agent mentions "TERMINATE".

    The example task requests booking a 3-day trip to New York, and the console
    displays the conversation stream between agents as they work to fulfill the request.

    Returns:
        None: Outputs the agent conversation to the console
    """

    async def lookup_hotel(location: str) -> str:
        return f"Here are some hotels in {location}: hotel1, hotel2, hotel3."

    async def lookup_flight(origin: str, destination: str) -> str:
        return f"Here are some flights from {origin} to {destination}: flight1, flight2, flight3."

    async def book_trip() -> str:
        return "Your trip is booked!"

    model_client = OpenAIChatCompletionClient(model="gpt-4o")

    travel_advisor = AssistantAgent(
        "Travel_Advisor",
        model_client,
        tools=[book_trip],
        description="Helps with travel planning.",
    )
    hotel_agent = AssistantAgent(
        "Hotel_Agent",
        model_client,
        tools=[lookup_hotel],
        description="Helps with hotel booking.",
    )
    flight_agent = AssistantAgent(
        "Flight_Agent",
        model_client,
        tools=[lookup_flight],
        description="Helps with flight booking.",
    )
    termination = TextMentionTermination("TERMINATE")
    team = SelectorGroupChat(
        [travel_advisor, hotel_agent, flight_agent],
        model_client=model_client,
        termination_condition=termination,
    )
    await team.reset()
    await Console(team.run_stream(task="Book a 3-day trip to new york."))


# --- Start the Chat ---
if __name__ == "__main__":
    asyncio.run(selector_team())

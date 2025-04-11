"""Factory for creating tools."""

from pathlib import Path
from autogen_ext.tools.langchain import LangChainToolAdapter
from autogen_ext.tools.mcp import StdioServerParams, mcp_server_tools
from .utilities.get_current_time import GetCurrentTime

from langchain_google_community import CalendarToolkit, GmailToolkit
from langchain_google_community.calendar.utils import (
    build_resource_service,
    get_google_credentials,
)

server_params = StdioServerParams(
    command="npx",
    args=[
        "-y",
        "@modelcontextprotocol/server-filesystem",
        str(Path.home() / "Desktop"),
    ],
)

fetch_mcp_server = StdioServerParams(command="uvx", args=["mcp-server-fetch"])


async def get_fetch_mcp_server():
    """Get the fetch MCP server."""
    return await mcp_server_tools(fetch_mcp_server)


async def get_file_system_tools():
    """Get the file system tools."""
    return await mcp_server_tools(server_params)


def get_google_calendar_tools(scopes: list[str]):
    """Get the Google Calendar tools."""
    # Can review scopes here: https://developers.google.com/calendar/api/auth
    # For instance, readonly scope is https://www.googleapis.com/auth/calendar.readonly
    credentials = get_google_credentials(
        scopes=scopes,
        token_file="token.json",
        client_secrets_file="credentials.json",
    )

    api_resource = build_resource_service(credentials=credentials)
    google_calendar_toolkit = CalendarToolkit(api_resource=api_resource)

    tools = google_calendar_toolkit.get_tools()

    autogen_tools = [
        LangChainToolAdapter(tool)
        for tool in tools
        if tool.name != "get_calendars_info"
    ]

    return autogen_tools


def get_google_gmail_tools(scopes: list[str]):
    """Get the Google Gmail tools."""
    credentials = get_google_credentials(
        scopes=["https://mail.google.com/"],
        token_file="token.json",
        client_secrets_file="credentials.json",
    )

    api_resource = build_resource_service(credentials=credentials)
    google_calendar_toolkit = GmailToolkit(api_resource=api_resource)

    tools = google_calendar_toolkit.get_tools()
    autogen_tools = [LangChainToolAdapter(tool) for tool in tools]
    return autogen_tools


def get_utility_tools():
    """Get the utility tools."""
    tools = [GetCurrentTime()]

    autogen_tools = [LangChainToolAdapter(tool) for tool in tools]

    return autogen_tools

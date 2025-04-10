"""Factory for creating tools."""

from pathlib import Path
from autogen_ext.tools.langchain import LangChainToolAdapter
from autogen_ext.tools.mcp import StdioServerParams, mcp_server_tools
from .utilities.get_current_time import GetCurrentTime

print(Path.home() / "Desktop")
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
    google_calendar_toolkit = GoogleCalendarToolkit(
        api_resource=build_google_calendar_resource_service(scopes=scopes)
    )
    tools = google_calendar_toolkit.get_tools()

    autogen_tools = [LangChainToolAdapter(tool) for tool in tools]

    return autogen_tools


def get_utility_tools():
    """Get the utility tools."""
    tools = [GetCurrentTime()]

    autogen_tools = [LangChainToolAdapter(tool) for tool in tools]

    return autogen_tools

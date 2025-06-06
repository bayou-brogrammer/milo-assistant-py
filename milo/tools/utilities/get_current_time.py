"""Tools for getting the current time."""

from datetime import datetime
from typing import Type

from dateutil import tz
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field


class TimeZoneInput(BaseModel):
    """Input for the GetCurrentTime tool."""

    timezone: str = Field(
        description="The timezone in TZ Database Name format, e.g. 'America/New_York'"
    )


class GetCurrentTime(BaseTool):
    """Get the current time based on timezone."""

    name: str = "get_current_time"
    description: str = (
        "Look up the current time based on timezone, returns %Y-%m-%d %H:%M:%S format"
    )
    args_schema: Type[BaseModel] = TimeZoneInput

    def _run(self, timezone: str) -> str:
        """Run the tool."""

        user_timezone = tz.gettz(timezone)
        now = datetime.now(tz=user_timezone)
        return now.strftime("%Y-%m-%d %H:%M:%S")

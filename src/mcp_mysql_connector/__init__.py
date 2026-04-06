__version__ = "0.1.0"
__all__ = ["mcp", "ConnectionManager", "run"]

from typing import TYPE_CHECKING

import mcp_mysql_connector.mcp as mcp_module
from mcp_mysql_connector.services.connection import (
    ConnectionManager,  # noqa: F401, E402
)

mcp = mcp_module.mcp


def run() -> None:
    """Run the MCP server."""
    mcp_module.mcp.run()


if TYPE_CHECKING:
    from mcp_mysql_connector.core.models import QueryResult, ServerStatus, TableSchema

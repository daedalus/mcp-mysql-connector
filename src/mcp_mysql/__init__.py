__version__ = "0.1.0"
__all__ = ["mcp", "ConnectionManager"]

from typing import TYPE_CHECKING

from mcp_mysql import mcp  # noqa: E402
from mcp_mysql.services.connection import ConnectionManager  # noqa: F401, E402

if TYPE_CHECKING:
    from mcp_mysql.core.models import QueryResult, ServerStatus, TableSchema

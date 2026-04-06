"""MCP MySQL Server.

This module provides the FastMCP server instance and registers all MySQL
tools and resources for the Model Context Protocol.

The server exposes the following tools:
- Connection management: connect, disconnect, is_connected
- Query execution: execute_query
- Database operations: list_databases, create_database, drop_database, database_exists
- Table operations: list_tables, describe_table, create_table, drop_table, table_exists
- Column/index operations: show_columns, show_indexes, create_index, drop_index
- User management: create_user, drop_user, grant_privileges, revoke_privileges, show_privileges
- Transaction control: commit, rollback
- Server information: server_status

It also provides resources for database and table metadata.
"""

from typing import Any

import fastmcp

from mcp_mysql_connector.tools import mysql_tools

mcp = fastmcp.FastMCP("mcp-mysql")

mcp.tool()(mysql_tools.connect)
mcp.tool()(mysql_tools.disconnect)
mcp.tool()(mysql_tools.execute_query)
mcp.tool()(mysql_tools.list_databases)
mcp.tool()(mysql_tools.list_tables)
mcp.tool()(mysql_tools.describe_table)
mcp.tool()(mysql_tools.create_database)
mcp.tool()(mysql_tools.drop_database)
mcp.tool()(mysql_tools.create_table)
mcp.tool()(mysql_tools.drop_table)
mcp.tool()(mysql_tools.show_columns)
mcp.tool()(mysql_tools.show_indexes)
mcp.tool()(mysql_tools.create_index)
mcp.tool()(mysql_tools.drop_index)
mcp.tool()(mysql_tools.create_user)
mcp.tool()(mysql_tools.drop_user)
mcp.tool()(mysql_tools.grant_privileges)
mcp.tool()(mysql_tools.revoke_privileges)
mcp.tool()(mysql_tools.show_privileges)
mcp.tool()(mysql_tools.server_status)
mcp.tool()(mysql_tools.table_exists)
mcp.tool()(mysql_tools.database_exists)
mcp.tool()(mysql_tools.commit)
mcp.tool()(mysql_tools.rollback)
mcp.tool()(mysql_tools.is_connected)


@mcp.resource("database://{name}")  # type: ignore[untyped-decorator]
def database_resource(name: str) -> dict[str, Any]:
    """Database metadata resource.

    Provides metadata about a specific database including its tables.

    Args:
        name: Database name.

    Returns:
        Dictionary containing:
            - name: Database name
            - tables: List of table names
            - table_count: Number of tables

    Example:
        >>> # Resource URL: database://mydb
        >>> {"name": "mydb", "tables": ["users", "orders"], "table_count": 2}
    """
    tables = mysql_tools.list_tables(name)
    return {
        "name": name,
        "tables": tables,
        "table_count": len(tables),
    }


@mcp.resource("table://{db}/{table}")  # type: ignore[untyped-decorator]
def table_resource(db: str, table: str) -> dict[str, Any]:
    """Table metadata resource.

    Provides comprehensive metadata about a table including schema,
    columns, and indexes.

    Args:
        db: Database name.
        table: Table name.

    Returns:
        Dictionary containing:
            - database: Database name
            - table: Table name
            - schema: Table schema information
            - columns: Column details
            - indexes: Index information

    Example:
        >>> # Resource URL: table://mydb/users
        >>> {"database": "mydb", "table": "users", "schema": {...}, ...}
    """
    schema = mysql_tools.describe_table(table, db)
    columns = mysql_tools.show_columns(table, db)
    indexes = mysql_tools.show_indexes(table, db)
    return {
        "database": db,
        "table": table,
        "schema": schema,
        "columns": columns,
        "indexes": indexes,
    }

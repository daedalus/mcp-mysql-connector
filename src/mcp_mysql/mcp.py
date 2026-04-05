from typing import Any

import fastmcp

from mcp_mysql.tools import mysql_tools

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


@mcp.resource("database://{name}")
def database_resource(name: str) -> dict[str, Any]:
    """Database metadata resource.

    Args:
        name: Database name.

    Returns:
        Database metadata.
    """
    tables = mysql_tools.list_tables(name)
    return {
        "name": name,
        "tables": tables,
        "table_count": len(tables),
    }


@mcp.resource("table://{db}/{table}")
def table_resource(db: str, table: str) -> dict[str, Any]:
    """Table metadata resource.

    Args:
        db: Database name.
        table: Table name.

    Returns:
        Table metadata including schema.
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

# MCP MySQL Connector

MCP server exposing MySQL database functionalities.

## When to use this skill

Use this skill when you need to:
- Connect to MySQL databases
- Execute queries
- Manage databases and tables
- Handle user authentication
- Perform schema introspection

## Tools

**Connection Management:**
- `connect`, `disconnect`, `is_connected`
- `commit`, `rollback`

**Query Execution:**
- `execute_query` - Execute raw SQL

**Database Operations:**
- `list_databases`, `create_database`, `drop_database`
- `database_exists`

**Table Operations:**
- `list_tables`, `describe_table`
- `create_table`, `drop_table`, `table_exists`

**Column & Index:**
- `show_columns`, `show_indexes`
- `create_index`, `drop_index`

**User Management:**
- `create_user`, `drop_user`
- `grant_privileges`, `revoke_privileges`, `show_privileges`

**Server Info:**
- `server_status`

## Install

```bash
pip install mcp-mysql-connector
```
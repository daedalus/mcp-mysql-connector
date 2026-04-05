# mcp-mysql

MCP server exposing MySQL database functionalities as tools.

[![PyPI](https://img.shields.io/pypi/v/mcp-mysql.svg)](https://pypi.org/project/mcp-mysql/)
[![Python](https://img.shields.io/pypi/pyversions/mcp-mysql.svg)](https://pypi.org/project/mcp-mysql/)

## Install

```bash
pip install mcp-mysql
```

## Usage

```python
from mcp_mysql import mcp

mcp.run()
```

## MCP Tools

The server exposes the following MySQL tools:

- `connect` - Connect to a MySQL database
- `disconnect` - Disconnect from MySQL
- `execute_query` - Execute raw SQL queries
- `list_databases` - List all databases
- `list_tables` - List tables in a database
- `describe_table` - Get table schema
- `create_database` - Create a database
- `drop_database` - Drop a database
- `create_table` - Create a table
- `drop_table` - Drop a table
- `show_columns` - Show table columns
- `show_indexes` - Show table indexes
- `create_index` - Create an index
- `drop_index` - Drop an index
- `create_user` - Create a MySQL user
- `drop_user` - Drop a MySQL user
- `grant_privileges` - Grant privileges
- `revoke_privileges` - Revoke privileges
- `show_privileges` - Show user privileges
- `server_status` - Get server status
- `table_exists` - Check if table exists
- `database_exists` - Check if database exists
- `commit` - Commit transaction
- `rollback` - Rollback transaction
- `is_connected` - Check connection status

## Development

```bash
git clone https://github.com/anomalyco/mcp-mysql.git
cd mcp-mysql
pip install -e ".[test]"

# run tests
pytest

# format
ruff format src/ tests/

# lint
ruff check src/ tests/

# type check
mypy src/
```

## mcp-name

`io.github.anomalyco/mcp-mysql`

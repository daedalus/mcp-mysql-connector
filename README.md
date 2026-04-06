# mcp-mysql-connector

MCP server exposing MySQL database functionalities as tools for LLM agents.

mcp-name: io.github.daedalus/mcp-mysql-connector


[![PyPI](https://img.shields.io/pypi/v/mcp-mysql-connector.svg)](https://pypi.org/project/mcp-mysql-connector/)
[![Python](https://img.shields.io/pypi/pyversions/mcp-mysql-connector.svg)](https://pypi.org/project/mcp-mysql-connector/)
[![Coverage](https://codecov.io/gh/daedalus/mcp-mysql-connector/branch/master/graph/badge.svg)](https://codecov.io/gh/daedalus/mcp-mysql-connector)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

## Overview

mcp-mysql-connector is a Model Context Protocol (MCP) server that provides MySQL database operations as tools for LLM agents. It allows AI assistants to interact with MySQL databases through a standardized protocol, enabling:

- Database and table management
- Query execution
- User authentication and privilege management
- Schema introspection
- Transaction control

## Install

```bash
pip install mcp-mysql-connector
```

## Quick Start

### Running the Server

```bash
# Run with stdio transport (default)
mcp-mysql-connector

# Or run programmatically
python -c "from mcp_mysql import mcp; mcp.run()"
```

### Configuration

Connect to MySQL using the `connect` tool:

```json
{
  "host": "localhost",
  "port": 3306,
  "user": "root",
  "password": "your_password",
  "database": "your_database"
}
```

## MCP Tools

### Connection Management

| Tool | Description |
|------|-------------|
| `connect` | Connect to a MySQL database |
| `disconnect` | Disconnect from MySQL |
| `is_connected` | Check connection status |
| `commit` | Commit current transaction |
| `rollback` | Rollback current transaction |

### Query Execution

| Tool | Description |
|------|-------------|
| `execute_query` | Execute raw SQL query and return results |

### Database Operations

| Tool | Description |
|------|-------------|
| `list_databases` | List all databases on server |
| `create_database` | Create a new database |
| `drop_database` | Drop a database |
| `database_exists` | Check if database exists |

### Table Operations

| Tool | Description |
|------|-------------|
| `list_tables` | List tables in a database |
| `describe_table` | Get table schema |
| `create_table` | Create a new table |
| `drop_table` | Drop a table |
| `table_exists` | Check if table exists |

### Column & Index Operations

| Tool | Description |
|------|-------------|
| `show_columns` | Show column details |
| `show_indexes` | Show index details |
| `create_index` | Create an index |
| `drop_index` | Drop an index |

### User Management

| Tool | Description |
|------|-------------|
| `create_user` | Create a MySQL user |
| `drop_user` | Drop a MySQL user |
| `grant_privileges` | Grant privileges to user |
| `revoke_privileges` | Revoke privileges from user |
| `show_privileges` | Show user privileges |

### Server Information

| Tool | Description |
|------|-------------|
| `server_status` | Get MySQL server status |

## MCP Resources

The server provides dynamic resources for database and table metadata:

- `database://{name}` - Database metadata including table list
- `table://{db}/{table}` - Table metadata including schema, columns, and indexes

## Usage Examples

### Connect and Query

```
# First, connect to database
connect(host="localhost", user="root", password="secret", database="mydb")

# Execute a query
execute_query(sql="SELECT * FROM users WHERE active = true")

# List all tables
list_tables(database="mydb")
```

### Create Database and Table

```
# Create a database
create_database(name="newapp")

# Create a table
create_table(name="users", schema="id INT PRIMARY KEY AUTO_INCREMENT, name VARCHAR(255), email VARCHAR(255) UNIQUE")
```

### User Management

```
# Create a new user with password
create_user(username="app_user", host="localhost", password="secure_password")

# Grant privileges
grant_privileges(privileges="SELECT,INSERT,UPDATE,DELETE", on="newapp.*", username="app_user", host="localhost")
```

### Transaction Control

```
# Start transaction
execute_query(sql="BEGIN")

# Execute operations
execute_query(sql="INSERT INTO accounts (balance) VALUES (100)")

# Commit or rollback
commit()  # or rollback()
```

## Environment Variables

The server supports configuration via environment variables:

```bash
export MYSQL_HOST=localhost
export MYSQL_PORT=3306
export MYSQL_USER=root
export MYSQL_PASSWORD=secret
export MYSQL_DATABASE=mydb
```

## Development

```bash
# Clone repository
git clone https://github.com/daedalus/mcp-mysql-connector.git
cd mcp-mysql-connector

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -e ".[test]"

# Run tests
pytest

# Format code
ruff format src/ tests/

# Lint
ruff check src/ tests/

# Type check
mypy src/
```

## Architecture

```
mcp-mysql-connector/
├── src/mcp_mysql/
│   ├── core/models.py       # Data models (QueryResult, TableSchema, etc.)
│   ├── adapters/mysql.py    # MySQL connection & pooling
│   ├── services/connection.py  # Connection manager
│   ├── tools/mysql_tools.py   # MCP tool implementations
│   └── mcp.py              # FastMCP server setup
└── tests/                   # Test suite
```

## Requirements

- Python 3.11+
- fastmcp >= 2.0.0
- pymysql >= 1.1.0
- sqlparse >= 0.4.0

## License

MIT License - see [LICENSE](LICENSE) for details.



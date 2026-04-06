# SPEC.md — mcp-mysql-connector

## Purpose
An MCP (Model Context Protocol) server that exposes MySQL database functionalities as tools for LLM agents. It allows executing queries, managing databases, tables, and performing administrative operations via the MCP protocol.

## Scope

### In Scope
- Connection management (connect, disconnect, pool)
- Query execution (SELECT, INSERT, UPDATE, DELETE)
- Database management (create, drop, show databases)
- Table management (create, drop, alter, show tables)
- Index management (create, drop indexes)
- User management (create, drop, grant, revoke users)
- Transaction support (commit, rollback)
- Schema introspection (describe, show columns, show indexes)
- Server status and health checks

### Not in Scope
- GUI/frontend components
- Migration tools
- ORM functionality
- Replication management

## Public API / Interface

### MCP Tools

| Tool Name | Description |
|-----------|-------------|
| `execute_query` | Execute a raw SQL query and return results |
| `list_databases` | List all databases on the server |
| `list_tables` | List all tables in a database |
| `describe_table` | Get table schema/structure |
| `create_database` | Create a new database |
| `drop_database` | Drop a database |
| `create_table` | Create a new table |
| `drop_table` | Drop a table |
| `show_columns` | Show columns of a table |
| `show_indexes` | Show indexes of a table |
| `create_index` | Create an index |
| `drop_index` | Drop an index |
| `create_user` | Create a new MySQL user |
| `drop_user` | Drop a MySQL user |
| `grant_privileges` | Grant privileges to a user |
| `revoke_privileges` | Revoke privileges from a user |
| `show_privileges` | Show user privileges |
| `server_status` | Get server status information |
| `table_exists` | Check if a table exists |
| `database_exists` | Check if a database exists |

### MCP Resources

| Resource URI | Description |
|--------------|-------------|
| `database://{name}` | Database metadata resource |
| `table://{db}/{table}` | Table metadata resource |

### Connection

The server supports connection via:
- Connection string (DSN)
- Individual connection parameters (host, port, user, password, database)

## Data Formats

### Query Results
```json
{
  "columns": ["col1", "col2"],
  "rows": [["value1", "value2"]],
  "affected_rows": 1
}
```

### Table Schema
```json
{
  "name": "users",
  "columns": [
    {"name": "id", "type": "int", "nullable": false, "key": "PRI"},
    {"name": "name", "type": "varchar(255)", "nullable": true, "key": ""}
  ]
}
```

## Edge Cases

1. **Connection failure**: Handle invalid credentials, unreachable host, timeout
2. **Query syntax errors**: Return MySQL error message clearly
3. **Empty results**: Return empty array, not null
4. **Large result sets**: Implement pagination/cursor support
5. **Transaction conflicts**: Handle deadlocks and lock wait timeouts
6. **Database/table not found**: Return clear error messages
7. **Permission denied**: Handle access control errors gracefully
8. **Concurrent connections**: Handle connection pool exhaustion
9. **Character encoding**: Support UTF-8 and handle encoding issues
10. **NULL values**: Handle NULL in query results correctly

## Performance & Constraints

- Connection pooling for efficiency
- Query timeout support (configurable)
- Max rows returned limit (configurable, default 1000)
- Connection timeout: 10 seconds default

## Dependencies

- `fastmcp` - MCP server framework
- `pymysql` - Pure Python MySQL driver
- `sqlparse` - SQL parsing utilities

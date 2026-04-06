from __future__ import annotations

from typing import Any

from mcp_mysql_connector.services.connection import ConnectionManager


def get_connection_manager() -> ConnectionManager:
    return ConnectionManager()


def connect(
    host: str = "localhost",
    port: int = 3306,
    user: str = "root",
    password: str = "",
    database: str = "",
    use_pool: bool = False,
    pool_size: int = 5,
) -> dict[str, Any]:
    """Connect to a MySQL database.

    Args:
        host: MySQL server hostname.
        port: MySQL server port.
        user: MySQL username.
        password: MySQL password.
        database: Default database to use.
        use_pool: Whether to use connection pooling.
        pool_size: Size of the connection pool.

    Returns:
        Connection status information.

    Example:
        >>> connect(host="localhost", user="root", password="secret", database="mydb")
        {"status": "connected", "host": "localhost", "port": 3306, "database": "mydb"}
    """
    cm = get_connection_manager()
    return cm.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        use_pool=use_pool,
        pool_size=pool_size,
    )


def disconnect() -> dict[str, Any]:
    """Disconnect from the MySQL database.

    Returns:
        Disconnection status.

    Example:
        >>> disconnect()
        {"status": "disconnected"}
    """
    cm = get_connection_manager()
    return cm.disconnect()


def execute_query(sql: str, params: dict | tuple | None = None) -> dict[str, Any]:
    """Execute a raw SQL query and return results.

    Args:
        sql: SQL query to execute.
        params: Optional parameters for the query.

    Returns:
        Query results with columns, rows, and affected row count.

    Example:
        >>> execute_query("SELECT * FROM users WHERE id = %s", (1,))
        {"columns": ["id", "name"], "rows": [[1, "John"]], "affected_rows": 0}
    """
    cm = get_connection_manager()
    return cm.execute(sql, params)


def list_databases() -> list[str]:
    """List all databases on the MySQL server.

    Returns:
        List of database names.

    Example:
        >>> list_databases()
        ["information_schema", "mysql", "testdb"]
    """
    cm = get_connection_manager()
    return cm.list_databases()


def list_tables(database: str | None = None) -> list[str]:
    """List all tables in a database.

    Args:
        database: Database name. If not specified, uses current database.

    Returns:
        List of table names.

    Example:
        >>> list_tables("mydb")
        ["users", "orders", "products"]
    """
    cm = get_connection_manager()
    return cm.list_tables(database)


def describe_table(table: str, database: str | None = None) -> dict[str, Any]:
    """Get the schema/structure of a table.

    Args:
        table: Table name.
        database: Database name. If not specified, uses current database.

    Returns:
        Table schema with column information.

    Example:
        >>> describe_table("users", "mydb")
        {"name": "users", "columns": [{"name": "id", "type": "int", "nullable": false, "key": "PRI", ...}]}
    """
    cm = get_connection_manager()
    return cm.describe_table(table, database)


def create_database(name: str, if_not_exists: bool = True) -> dict[str, Any]:
    """Create a new database.

    Args:
        name: Database name.
        if_not_exists: Use IF NOT EXISTS clause.

    Returns:
        Creation status.

    Example:
        >>> create_database("newdb")
        {"status": "created", "database": "newdb"}
    """
    cm = get_connection_manager()
    return cm.create_database(name, if_not_exists)


def drop_database(name: str, if_exists: bool = True) -> dict[str, Any]:
    """Drop a database.

    Args:
        name: Database name.
        if_exists: Use IF EXISTS clause.

    Returns:
        Drop status.

    Example:
        >>> drop_database("olddb")
        {"status": "dropped", "database": "olddb"}
    """
    cm = get_connection_manager()
    return cm.drop_database(name, if_exists)


def create_table(name: str, schema: str) -> dict[str, Any]:
    """Create a new table.

    Args:
        name: Table name.
        schema: SQL CREATE TABLE statement (without CREATE TABLE part).

    Returns:
        Creation status.

    Example:
        >>> create_table("users", "id INT PRIMARY KEY, name VARCHAR(255)")
        {"status": "created", "table": "users"}
    """
    cm = get_connection_manager()
    cm.execute(f"CREATE TABLE `{name}` {schema}")
    return {"status": "created", "table": name}


def drop_table(name: str, if_exists: bool = True) -> dict[str, Any]:
    """Drop a table.

    Args:
        name: Table name.
        if_exists: Use IF EXISTS clause.

    Returns:
        Drop status.

    Example:
        >>> drop_table("old_table")
        {"status": "dropped", "table": "old_table"}
    """
    cm = get_connection_manager()
    if if_exists:
        cm.execute(f"DROP TABLE IF EXISTS `{name}`")
    else:
        cm.execute(f"DROP TABLE `{name}`")
    return {"status": "dropped", "table": name}


def show_columns(table: str, database: str | None = None) -> list[dict[str, Any]]:
    """Show columns of a table.

    Args:
        table: Table name.
        database: Database name.

    Returns:
        List of column information.

    Example:
        >>> show_columns("users", "mydb")
        [{"field": "id", "type": "int", "null": "NO", "key": "PRI", ...}]
    """
    cm = get_connection_manager()
    return cm.show_columns(table, database)


def show_indexes(table: str, database: str | None = None) -> list[dict[str, Any]]:
    """Show indexes of a table.

    Args:
        table: Table name.
        database: Database name.

    Returns:
        List of index information.

    Example:
        >>> show_indexes("users", "mydb")
        [{"table": "users", "non_unique": 0, "key_name": "PRIMARY", ...}]
    """
    cm = get_connection_manager()
    return cm.show_indexes(table, database)


def create_index(
    name: str,
    table: str,
    columns: str,
    index_type: str = "BTREE",
    database: str | None = None,
) -> dict[str, Any]:
    """Create an index on a table.

    Args:
        name: Index name.
        table: Table name.
        columns: Column(s) to index.
        index_type: Index type (BTREE, HASH, etc.).
        database: Database name.

    Returns:
        Creation status.

    Example:
        >>> create_index("idx_name", "users", "name", "BTREE", "mydb")
        {"status": "created", "index": "idx_name"}
    """
    cm = get_connection_manager()
    if database:
        cm.execute(f"USE `{database}`")
    cm.execute(f"CREATE INDEX `{name}` ON `{table}` ({columns}) USING {index_type}")
    return {"status": "created", "index": name}


def drop_index(name: str, table: str, database: str | None = None) -> dict[str, Any]:
    """Drop an index from a table.

    Args:
        name: Index name.
        table: Table name.
        database: Database name.

    Returns:
        Drop status.

    Example:
        >>> drop_index("idx_name", "users", "mydb")
        {"status": "dropped", "index": "idx_name"}
    """
    cm = get_connection_manager()
    if database:
        cm.execute(f"USE `{database}`")
    cm.execute(f"DROP INDEX `{name}` ON `{table}`")
    return {"status": "dropped", "index": name}


def create_user(
    username: str, host: str = "%", password: str | None = None
) -> dict[str, Any]:
    """Create a new MySQL user.

    Args:
        username: Username.
        host: Host (default: %).
        password: Optional password.

    Returns:
        Creation status.

    Example:
        >>> create_user("newuser", "localhost", "password123")
        {"status": "created", "user": "newuser@localhost"}
    """
    cm = get_connection_manager()
    return cm.create_user(username, host, password)


def drop_user(username: str, host: str = "%") -> dict[str, Any]:
    """Drop a MySQL user.

    Args:
        username: Username.
        host: Host (default: %).

    Returns:
        Drop status.

    Example:
        >>> drop_user("olduser", "localhost")
        {"status": "dropped", "user": "olduser@localhost"}
    """
    cm = get_connection_manager()
    return cm.drop_user(username, host)


def grant_privileges(
    privileges: str, on: str, username: str, host: str = "%"
) -> dict[str, Any]:
    """Grant privileges to a user.

    Args:
        privileges: Privileges to grant (e.g., SELECT, INSERT, ALL).
        on: Database.table to grant on (e.g., mydb.*).
        username: Username.
        host: Host (default: %).

    Returns:
        Grant status.

    Example:
        >>> grant_privileges("SELECT,INSERT", "mydb.*", "newuser", "localhost")
        {"status": "granted", "privileges": "SELECT,INSERT", "on": "mydb.*", "to": "newuser@localhost"}
    """
    cm = get_connection_manager()
    return cm.grant_privileges(privileges, on, username, host)


def revoke_privileges(
    privileges: str, on: str, username: str, host: str = "%"
) -> dict[str, Any]:
    """Revoke privileges from a user.

    Args:
        privileges: Privileges to revoke.
        on: Database.table to revoke from.
        username: Username.
        host: Host (default: %).

    Returns:
        Revoke status.

    Example:
        >>> revoke_privileges("INSERT", "mydb.*", "user", "localhost")
        {"status": "revoked", "privileges": "INSERT", "on": "mydb.*", "from": "user@localhost"}
    """
    cm = get_connection_manager()
    return cm.revoke_privileges(privileges, on, username, host)


def show_privileges(username: str, host: str = "%") -> list[str]:
    """Show privileges for a user.

    Args:
        username: Username.
        host: Host (default: %).

    Returns:
        List of grants.

    Example:
        >>> show_privileges("newuser", "localhost")
        ["GRANT SELECT ON *.* TO 'newuser'@'localhost'"]
    """
    cm = get_connection_manager()
    return cm.show_grants(username, host)


def server_status() -> dict[str, Any]:
    """Get MySQL server status information.

    Returns:
        Server status data.

    Example:
        >>> server_status()
        {"version": "8.0.30", "uptime": 12345, "threads": 2, ...}
    """
    cm = get_connection_manager()
    return cm.server_status()


def table_exists(table: str, database: str | None = None) -> bool:
    """Check if a table exists.

    Args:
        table: Table name.
        database: Database name.

    Returns:
        True if table exists, False otherwise.

    Example:
        >>> table_exists("users", "mydb")
        True
    """
    cm = get_connection_manager()
    return cm.table_exists(table, database)


def database_exists(name: str) -> bool:
    """Check if a database exists.

    Args:
        name: Database name.

    Returns:
        True if database exists, False otherwise.

    Example:
        >>> database_exists("mydb")
        True
    """
    cm = get_connection_manager()
    return cm.database_exists(name)


def commit() -> dict[str, str]:
    """Commit the current transaction.

    Returns:
        Commit status.

    Example:
        >>> commit()
        {"status": "committed"}
    """
    cm = get_connection_manager()
    cm.commit()
    return {"status": "committed"}


def rollback() -> dict[str, str]:
    """Rollback the current transaction.

    Returns:
        Rollback status.

    Example:
        >>> rollback()
        {"status": "rolledback"}
    """
    cm = get_connection_manager()
    cm.rollback()
    return {"status": "rolledback"}


def is_connected() -> bool:
    """Check if connected to MySQL.

    Returns:
        Connection status.

    Example:
        >>> is_connected()
        True
    """
    cm = get_connection_manager()
    return cm.is_connected

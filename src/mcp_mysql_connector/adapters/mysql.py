"""MySQL database adapter for MCP server.

This module provides the MySQLConnection and ConnectionPool classes for
interacting with MySQL databases using the pymysql driver.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING, Any

import pymysql
from pymysql.cursors import DictCursor

from mcp_mysql_connector.core.models import ColumnInfo, QueryResult, ServerStatus, TableSchema

if TYPE_CHECKING:
    from collections.abc import Generator


class MySQLConnection:
    """MySQL database connection handler.

    Provides methods for executing queries, managing databases, tables,
    and performing administrative operations on a MySQL server.

    Attributes:
        config: Dictionary containing connection parameters.
        _connection: Internal pymysql connection object.

    Example:
        >>> conn = MySQLConnection(host="localhost", user="root", password="secret")
        >>> conn.connect()
        >>> result = conn.execute("SELECT * FROM users")
        >>> conn.close()
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 3306,
        user: str = "root",
        password: str = "",
        database: str = "",
        charset: str = "utf8mb4",
        connect_timeout: int = 10,
    ) -> None:
        """Initialize MySQL connection with parameters.

        Args:
            host: MySQL server hostname or IP address.
            port: MySQL server port (default: 3306).
            user: MySQL username.
            password: MySQL password.
            database: Default database to connect to.
            charset: Character encoding (default: utf8mb4).
            connect_timeout: Connection timeout in seconds (default: 10).
        """
        self.config: dict[str, str | int] = {
            "host": host,
            "port": port,
            "user": user,
            "password": password,
            "database": database,
            "charset": charset,
            "connect_timeout": connect_timeout,
            "cursorclass": DictCursor,
        }
        self._connection: pymysql.Connection | None = None

    def connect(self) -> None:
        """Establish connection to MySQL server.

        Establishes a new connection to the MySQL server using the
        configuration parameters provided during initialization.

        Example:
            >>> conn = MySQLConnection(host="localhost", user="root")
            >>> conn.connect()
        """
        self._connection = pymysql.connect(**self.config)

    def close(self) -> None:
        """Close the MySQL connection.

        Closes the current connection and sets the internal connection
        reference to None.

        Example:
            >>> conn.connect()
            >>> conn.close()
        """
        if self._connection:
            self._connection.close()
            self._connection = None

    @property
    def is_connected(self) -> bool:
        """Check if connection is active.

        Returns:
            True if connected to MySQL server, False otherwise.

        Example:
            >>> conn.connect()
            >>> conn.is_connected
            True
        """
        return self._connection is not None and self._connection.open

    @contextmanager
    def cursor(self) -> Generator[DictCursor, None, None]:
        """Get a database cursor as a context manager.

        Creates a new cursor for executing queries. If no connection
        exists, automatically establishes one before creating the cursor.
        The cursor is automatically closed when exiting the context.

        Yields:
            DictCursor: A dictionary cursor for query execution.

        Example:
            >>> with conn.cursor() as cur:
            ...     cur.execute("SELECT * FROM users")
        """
        if not self._connection:
            self.connect()
        cursor = self._connection.cursor()
        try:
            yield cursor
        finally:
            cursor.close()

    def execute(self, sql: str, params: tuple | dict | None = None) -> QueryResult:
        """Execute a SQL query.

        Executes the given SQL statement with optional parameters and
        returns the query results.

        Args:
            sql: SQL statement to execute.
            params: Optional parameters for parameterized queries.

        Returns:
            QueryResult containing columns, rows, and affected row count.

        Example:
            >>> result = conn.execute("SELECT * FROM users WHERE id = %s", (1,))
            >>> result.columns
            ['id', 'name']
        """
        with self.cursor() as cur:
            cur.execute(sql, params)
            if cur.description:
                columns = [desc[0] for desc in cur.description]
                rows = [list(row.values()) for row in cur.fetchall()]
                return QueryResult(
                    columns=columns,
                    rows=rows,
                    affected_rows=cur.rowcount,
                )
            return QueryResult(columns=[], rows=[], affected_rows=cur.rowcount)

    def execute_many(self, sql: str, params_list: list[tuple | dict]) -> int:
        """Execute a SQL statement multiple times with different parameters.

        Uses executemany to efficiently execute the same SQL statement
        with multiple parameter sets.

        Args:
            sql: SQL statement template.
            params_list: List of parameter tuples/dicts.

        Returns:
            Number of rows affected.

        Example:
            >>> conn.execute_many("INSERT INTO users (name) VALUES (%s)", [("Alice",), ("Bob",)])
            2
        """
        with self.cursor() as cur:
            cur.executemany(sql, params_list)
            return cur.rowcount

    def commit(self) -> None:
        """Commit the current transaction.

        Saves all changes made during the current transaction to the database.

        Example:
            >>> conn.execute("INSERT INTO users (name) VALUES ('Alice')")
            >>> conn.commit()
        """
        if self._connection:
            self._connection.commit()

    def rollback(self) -> None:
        """Rollback the current transaction.

        Discards all changes made during the current transaction.

        Example:
            >>> conn.execute("INSERT INTO users (name) VALUES ('Alice')")
            >>> conn.rollback()
        """
        if self._connection:
            self._connection.rollback()

    def list_databases(self) -> list[str]:
        """List all databases on the MySQL server.

        Returns:
            List of database names.

        Example:
            >>> conn.list_databases()
            ['information_schema', 'mysql', 'testdb']
        """
        result = self.execute("SHOW DATABASES")
        return [row[0] for row in result.rows]

    def list_tables(self, database: str | None = None) -> list[str]:
        """List all tables in a database.

        Args:
            database: Database name. If None, lists tables in current database.

        Returns:
            List of table names.

        Example:
            >>> conn.list_tables("mydb")
            ['users', 'orders', 'products']
        """
        if database:
            self.execute(f"USE `{database}`")
        result = self.execute("SHOW TABLES")
        return [row[0] for row in result.rows]

    def describe_table(self, table: str, database: str | None = None) -> TableSchema:
        """Get the schema of a table.

        Args:
            table: Table name.
            database: Database name. If None, uses current database.

        Returns:
            TableSchema containing table name and column information.

        Example:
            >>> schema = conn.describe_table("users", "mydb")
            >>> schema.name
            'users'
        """
        if database:
            self.execute(f"USE `{database}`")
        result = self.execute(f"DESCRIBE `{table}`")
        columns = [
            ColumnInfo(
                name=row[0],
                type=row[1],
                nullable=row[2] == "YES",
                key=row[3],
                default=row[4],
                extra=row[5],
            )
            for row in result.rows
        ]
        return TableSchema(name=table, columns=columns)

    def show_columns(
        self, table: str, database: str | None = None
    ) -> list[dict[str, Any]]:
        """Show detailed column information for a table.

        Args:
            table: Table name.
            database: Database name. If None, uses current database.

        Returns:
            List of dictionaries containing column metadata.

        Example:
            >>> conn.show_columns("users", "mydb")
            [{'field': 'id', 'type': 'int', 'null': 'NO', ...}]
        """
        if database:
            self.execute(f"USE `{database}`")
        result = self.execute(f"SHOW COLUMNS FROM `{table}`")
        return [
            {
                "field": row[0],
                "type": row[1],
                "null": row[2],
                "key": row[3],
                "default": row[4],
                "extra": row[5],
            }
            for row in result.rows
        ]

    def show_indexes(
        self, table: str, database: str | None = None
    ) -> list[dict[str, Any]]:
        """Show index information for a table.

        Args:
            table: Table name.
            database: Database name. If None, uses current database.

        Returns:
            List of dictionaries containing index metadata.

        Example:
            >>> conn.show_indexes("users", "mydb")
            [{'key_name': 'PRIMARY', 'column_name': 'id', ...}]
        """
        if database:
            self.execute(f"USE `{database}`")
        result = self.execute(f"SHOW INDEXES FROM `{table}`")
        return [
            {
                "table": row[0],
                "non_unique": row[1],
                "key_name": row[2],
                "seq_in_index": row[3],
                "column_name": row[4],
                "cardinality": row[5],
            }
            for row in result.rows
        ]

    def create_database(self, name: str, if_not_exists: bool = True) -> None:
        """Create a new database.

        Args:
            name: Database name.
            if_not_exists: Use IF NOT EXISTS clause (default: True).

        Example:
            >>> conn.create_database("newdb")
            >>> conn.create_database("newdb", if_not_exists=False)
        """
        if if_not_exists:
            self.execute(f"CREATE DATABASE IF NOT EXISTS `{name}`")
        else:
            self.execute(f"CREATE DATABASE `{name}`")

    def drop_database(self, name: str, if_exists: bool = True) -> None:
        """Drop (delete) a database.

        Args:
            name: Database name.
            if_exists: Use IF EXISTS clause (default: True).

        Example:
            >>> conn.drop_database("olddb")
            >>> conn.drop_database("olddb", if_exists=False)
        """
        if if_exists:
            self.execute(f"DROP DATABASE IF EXISTS `{name}`")
        else:
            self.execute(f"DROP DATABASE `{name}`")

    def database_exists(self, name: str) -> bool:
        """Check if a database exists.

        Args:
            name: Database name.

        Returns:
            True if database exists, False otherwise.

        Example:
            >>> conn.database_exists("mydb")
            True
        """
        result = self.execute(
            "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = %s",
            (name,),
        )
        return len(result.rows) > 0

    def table_exists(self, table: str, database: str | None = None) -> bool:
        """Check if a table exists.

        Args:
            table: Table name.
            database: Database name.

        Returns:
            True if table exists, False otherwise.

        Example:
            >>> conn.table_exists("users", "mydb")
            True
        """
        if database:
            query = """
                SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_NAME = %s AND TABLE_SCHEMA = %s
            """
            result = self.execute(query, (table, database))
        else:
            result = self.execute("SHOW TABLES LIKE %s", (table,))
        return len(result.rows) > 0

    def create_user(
        self, username: str, host: str = "%", password: str | None = None
    ) -> None:
        """Create a new MySQL user.

        Args:
            username: Username.
            host: Host (default: '%' for any host).
            password: Optional password.

        Example:
            >>> conn.create_user("newuser", "localhost", "password123")
            >>> conn.create_user("newuser", "localhost", None)
        """
        if password:
            self.execute(
                f"CREATE USER '{username}'@'{host}' IDENTIFIED BY %s", (password,)
            )
        else:
            self.execute(f"CREATE USER '{username}'@'{host}'")

    def drop_user(self, username: str, host: str = "%") -> None:
        """Drop (delete) a MySQL user.

        Args:
            username: Username.
            host: Host (default: '%').

        Example:
            >>> conn.drop_user("olduser", "localhost")
        """
        self.execute(f"DROP USER '{username}'@'{host}'")

    def grant_privileges(
        self, privileges: str, on: str, username: str, host: str = "%"
    ) -> None:
        """Grant privileges to a MySQL user.

        Args:
            privileges: Comma-separated list of privileges (e.g., 'SELECT,INSERT').
            on: Database.table pattern (e.g., 'mydb.*').
            username: Username.
            host: Host (default: '%').

        Example:
            >>> conn.grant_privileges("SELECT,INSERT", "mydb.*", "user", "localhost")
        """
        self.execute(f"GRANT {privileges} ON {on} TO '{username}'@'{host}'")
        self.execute("FLUSH PRIVILEGES")

    def revoke_privileges(
        self, privileges: str, on: str, username: str, host: str = "%"
    ) -> None:
        """Revoke privileges from a MySQL user.

        Args:
            privileges: Comma-separated list of privileges.
            on: Database.table pattern.
            username: Username.
            host: Host (default: '%').

        Example:
            >>> conn.revoke_privileges("INSERT", "mydb.*", "user", "localhost")
        """
        self.execute(f"REVOKE {privileges} ON {on} FROM '{username}'@'{host}'")
        self.execute("FLUSH PRIVILEGES")

    def show_grants(self, username: str, host: str = "%") -> list[str]:
        """Show granted privileges for a user.

        Args:
            username: Username.
            host: Host (default: '%').

        Returns:
            List of GRANT statements.

        Example:
            >>> conn.show_grants("user", "localhost")
            ["GRANT SELECT ON *.* TO 'user'@'localhost'"]
        """
        result = self.execute(f"SHOW GRANTS FOR '{username}'@'{host}'")
        return [row[0] for row in result.rows]

    def server_status(self) -> ServerStatus:
        """Get MySQL server status information.

        Returns:
            ServerStatus object containing server metrics.

        Example:
            >>> status = conn.server_status()
            >>> status.version
            '8.0.30'
        """
        result = self.execute("SHOW STATUS LIKE 'Uptime'")
        uptime = int(result.rows[0][1]) if result.rows else 0

        result = self.execute("SHOW STATUS LIKE 'Threads_connected'")
        threads = int(result.rows[0][1]) if result.rows else 0

        result = self.execute("SHOW GLOBAL STATUS LIKE 'Questions'")
        questions = int(result.rows[0][1]) if result.rows else 0

        result = self.execute("SHOW GLOBAL STATUS LIKE 'Slow_queries'")
        slow_queries = int(result.rows[0][1]) if result.rows else 0

        result = self.execute("SHOW GLOBAL STATUS LIKE 'Opens'")
        opens = int(result.rows[0][1]) if result.rows else 0

        result = self.execute("SHOW GLOBAL STATUS LIKE 'Flush_tables'")
        flush_tables = int(result.rows[0][1]) if result.rows else 0

        result = self.execute("SHOW GLOBAL STATUS LIKE 'Open_tables'")
        open_tables = int(result.rows[0][1]) if result.rows else 0

        result = self.execute("SELECT VERSION()")
        version = result.rows[0][0] if result.rows else "unknown"

        return ServerStatus(
            version=version,
            uptime=uptime,
            threads=threads,
            questions=questions,
            slow_queries=slow_queries,
            opens=opens,
            flush_tables=flush_tables,
            open_tables=open_tables,
        )


class ConnectionPool:
    """MySQL connection pool for managing multiple connections.

    Provides a pool of reusable MySQL connections to improve performance
    when handling multiple database operations.

    Attributes:
        config: Dictionary containing connection parameters.
        pool_size: Maximum number of connections in the pool.
        _pool: Internal list of available connections.

    Example:
        >>> pool = ConnectionPool(host="localhost", user="root", pool_size=5)
        >>> conn = pool.get_connection()
        >>> # ... use connection ...
        >>> pool.return_connection(conn)
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 3306,
        user: str = "root",
        password: str = "",
        database: str = "",
        pool_size: int = 5,
    ) -> None:
        """Initialize connection pool.

        Args:
            host: MySQL server hostname.
            port: MySQL server port.
            user: MySQL username.
            password: MySQL password.
            database: Default database.
            pool_size: Maximum connections in pool (default: 5).
        """
        self.config: dict[str, str | int] = {
            "host": host,
            "port": port,
            "user": user,
            "password": password,
            "database": database,
        }
        self.pool_size = pool_size
        self._pool: list[MySQLConnection] = []

    def get_connection(self) -> MySQLConnection:
        """Get a connection from the pool or create a new one.

        If an existing connection in the pool is connected, it will be
        returned. Otherwise, a new connection is created.

        Returns:
            MySQLConnection: A ready-to-use connection.

        Example:
            >>> conn = pool.get_connection()
        """
        if self._pool:
            conn = self._pool.pop()
            if conn.is_connected:
                return conn
        conn = MySQLConnection(
            host=str(self.config["host"]),
            port=int(self.config["port"]),
            user=str(self.config["user"]),
            password=str(self.config["password"]),
            database=str(self.config["database"]),
        )
        conn.connect()
        return conn

    def return_connection(self, conn: MySQLConnection) -> None:
        """Return a connection to the pool.

        If the pool is not full, the connection is added back to the
        pool. Otherwise, the connection is closed.

        Args:
            conn: Connection to return to the pool.

        Example:
            >>> pool.return_connection(conn)
        """
        if len(self._pool) < self.pool_size:
            self._pool.append(conn)
        else:
            conn.close()

    def close_all(self) -> None:
        """Close all connections in the pool.

        Example:
            >>> pool.close_all()
        """
        for conn in self._pool:
            conn.close()
        self._pool.clear()

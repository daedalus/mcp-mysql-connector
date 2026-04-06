"""Connection management service for MCP MySQL server.

This module provides the ConnectionManager class which serves as a singleton
for managing MySQL connections across the MCP server. It provides a simplified
interface for common database operations.
"""

from __future__ import annotations

from typing import Any

from mcp_mysql.adapters.mysql import ConnectionPool, MySQLConnection


class ConnectionManager:
    """Singleton connection manager for MySQL operations.

    This class provides a centralized way to manage MySQL connections
    throughout the MCP server. It uses the singleton pattern to ensure
    only one connection manager exists at a time.

    Attributes:
        _instance: Singleton instance of ConnectionManager.
        _connection: Current MySQL connection.
        _pool: Optional connection pool.

    Example:
        >>> cm = ConnectionManager()
        >>> cm.connect(host="localhost", user="root", password="secret")
        >>> result = cm.execute("SELECT * FROM users")
        >>> cm.disconnect()
    """

    _instance: ConnectionManager | None = None

    def __new__(cls) -> ConnectionManager:
        """Create or return the singleton ConnectionManager instance.

        Returns:
            The singleton ConnectionManager instance.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._connection = None
            cls._instance._pool = None
        return cls._instance

    def connect(
        self,
        host: str = "localhost",
        port: int = 3306,
        user: str = "root",
        password: str = "",
        database: str = "",
        use_pool: bool = False,
        pool_size: int = 5,
    ) -> dict[str, str]:
        """Connect to a MySQL database.

        Establishes a connection to the MySQL server. If an existing
        connection is active, it will be closed before creating a new one.

        Args:
            host: MySQL server hostname (default: localhost).
            port: MySQL server port (default: 3306).
            user: MySQL username (default: root).
            password: MySQL password (default: empty).
            database: Default database to connect to (default: empty).
            use_pool: Whether to enable connection pooling (default: False).
            pool_size: Size of connection pool if enabled (default: 5).

        Returns:
            Dictionary with connection status information.

        Example:
            >>> cm.connect(host="localhost", user="root", password="secret", database="mydb")
            {"status": "connected", "host": "localhost", "port": 3306, "database": "mydb"}
        """
        if self._connection and self._connection.is_connected:
            self._connection.close()

        self._connection = MySQLConnection(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
        )
        self._connection.connect()

        if use_pool:
            self._pool = ConnectionPool(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database,
                pool_size=pool_size,
            )

        return {"status": "connected", "host": host, "port": port, "database": database}

    def disconnect(self) -> dict[str, str]:
        """Disconnect from MySQL database.

        Closes the current connection and optionally closes the connection
        pool if one was created.

        Returns:
            Dictionary with disconnection status.

        Example:
            >>> cm.disconnect()
            {"status": "disconnected"}
        """
        if self._connection:
            self._connection.close()
            self._connection = None
        if self._pool:
            self._pool.close_all()
            self._pool = None
        return {"status": "disconnected"}

    @property
    def is_connected(self) -> bool:
        """Check if currently connected to MySQL.

        Returns:
            True if connected, False otherwise.

        Example:
            >>> cm.is_connected
            True
        """
        return self._connection is not None and self._connection.is_connected

    def get_connection(self) -> MySQLConnection:
        """Get the current MySQL connection.

        Returns:
            The current MySQLConnection instance.

        Raises:
            RuntimeError: If not connected to MySQL.

        Example:
            >>> conn = cm.get_connection()
        """
        if not self._connection or not self._connection.is_connected:
            raise RuntimeError("Not connected to MySQL. Call connect() first.")
        return self._connection

    def execute(self, sql: str, params: tuple | dict | None = None) -> dict[str, Any]:
        """Execute a SQL query.

        Args:
            sql: SQL statement to execute.
            params: Optional parameters for parameterized queries.

        Returns:
            Dictionary containing query results.

        Example:
            >>> cm.execute("SELECT * FROM users WHERE id = %s", (1,))
            {"columns": ["id", "name"], "rows": [[1, "Alice"]], "affected_rows": 0}
        """
        conn = self.get_connection()
        result = conn.execute(sql, params)
        return result.to_dict()

    def commit(self) -> None:
        """Commit the current transaction.

        Example:
            >>> cm.execute("INSERT INTO users (name) VALUES ('Alice')")
            >>> cm.commit()
        """
        conn = self.get_connection()
        conn.commit()

    def rollback(self) -> None:
        """Rollback the current transaction.

        Example:
            >>> cm.rollback()
        """
        conn = self.get_connection()
        conn.rollback()

    def list_databases(self) -> list[str]:
        """List all databases on the server.

        Returns:
            List of database names.

        Example:
            >>> cm.list_databases()
            ["information_schema", "mysql", "testdb"]
        """
        conn = self.get_connection()
        return conn.list_databases()

    def list_tables(self, database: str | None = None) -> list[str]:
        """List all tables in a database.

        Args:
            database: Database name. If None, uses current database.

        Returns:
            List of table names.

        Example:
            >>> cm.list_tables("mydb")
            ["users", "orders", "products"]
        """
        conn = self.get_connection()
        return conn.list_tables(database)

    def describe_table(self, table: str, database: str | None = None) -> dict[str, Any]:
        """Get table schema.

        Args:
            table: Table name.
            database: Database name. If None, uses current database.

        Returns:
            Dictionary containing table schema.

        Example:
            >>> cm.describe_table("users", "mydb")
            {"name": "users", "columns": [...]}
        """
        conn = self.get_connection()
        schema = conn.describe_table(table, database)
        return schema.to_dict()

    def show_columns(
        self, table: str, database: str | None = None
    ) -> list[dict[str, Any]]:
        """Show table columns.

        Args:
            table: Table name.
            database: Database name.

        Returns:
            List of column information dictionaries.

        Example:
            >>> cm.show_columns("users", "mydb")
            [{"field": "id", "type": "int", ...}]
        """
        conn = self.get_connection()
        return conn.show_columns(table, database)

    def show_indexes(
        self, table: str, database: str | None = None
    ) -> list[dict[str, Any]]:
        """Show table indexes.

        Args:
            table: Table name.
            database: Database name.

        Returns:
            List of index information dictionaries.

        Example:
            >>> cm.show_indexes("users", "mydb")
            [{"key_name": "PRIMARY", ...}]
        """
        conn = self.get_connection()
        return conn.show_indexes(table, database)

    def create_database(self, name: str, if_not_exists: bool = True) -> dict[str, Any]:
        """Create a database.

        Args:
            name: Database name.
            if_not_exists: Use IF NOT EXISTS clause.

        Returns:
            Dictionary with creation status.

        Example:
            >>> cm.create_database("newdb")
            {"status": "created", "database": "newdb"}
        """
        conn = self.get_connection()
        conn.create_database(name, if_not_exists)
        return {"status": "created", "database": name}

    def drop_database(self, name: str, if_exists: bool = True) -> dict[str, Any]:
        """Drop a database.

        Args:
            name: Database name.
            if_exists: Use IF EXISTS clause.

        Returns:
            Dictionary with drop status.

        Example:
            >>> cm.drop_database("olddb")
            {"status": "dropped", "database": "olddb"}
        """
        conn = self.get_connection()
        conn.drop_database(name, if_exists)
        return {"status": "dropped", "database": name}

    def database_exists(self, name: str) -> bool:
        """Check if a database exists.

        Args:
            name: Database name.

        Returns:
            True if database exists, False otherwise.

        Example:
            >>> cm.database_exists("mydb")
            True
        """
        conn = self.get_connection()
        return conn.database_exists(name)

    def table_exists(self, table: str, database: str | None = None) -> bool:
        """Check if a table exists.

        Args:
            table: Table name.
            database: Database name.

        Returns:
            True if table exists, False otherwise.

        Example:
            >>> cm.table_exists("users", "mydb")
            True
        """
        conn = self.get_connection()
        return conn.table_exists(table, database)

    def create_user(
        self, username: str, host: str = "%", password: str | None = None
    ) -> dict[str, Any]:
        """Create a MySQL user.

        Args:
            username: Username.
            host: Host (default: '%').
            password: Optional password.

        Returns:
            Dictionary with creation status.

        Example:
            >>> cm.create_user("newuser", "localhost", "password123")
            {"status": "created", "user": "newuser@localhost"}
        """
        conn = self.get_connection()
        conn.create_user(username, host, password)
        return {"status": "created", "user": f"{username}@{host}"}

    def drop_user(self, username: str, host: str = "%") -> dict[str, Any]:
        """Drop a MySQL user.

        Args:
            username: Username.
            host: Host (default: '%').

        Returns:
            Dictionary with drop status.

        Example:
            >>> cm.drop_user("olduser", "localhost")
            {"status": "dropped", "user": "olduser@localhost"}
        """
        conn = self.get_connection()
        conn.drop_user(username, host)
        return {"status": "dropped", "user": f"{username}@{host}"}

    def grant_privileges(
        self, privileges: str, on: str, username: str, host: str = "%"
    ) -> dict[str, Any]:
        """Grant privileges to a user.

        Args:
            privileges: Privileges to grant.
            on: Database.table pattern.
            username: Username.
            host: Host (default: '%').

        Returns:
            Dictionary with grant status.

        Example:
            >>> cm.grant_privileges("SELECT,INSERT", "mydb.*", "user", "localhost")
            {"status": "granted", "privileges": "SELECT,INSERT", ...}
        """
        conn = self.get_connection()
        conn.grant_privileges(privileges, on, username, host)
        return {
            "status": "granted",
            "privileges": privileges,
            "on": on,
            "to": f"{username}@{host}",
        }

    def revoke_privileges(
        self, privileges: str, on: str, username: str, host: str = "%"
    ) -> dict[str, Any]:
        """Revoke privileges from a user.

        Args:
            privileges: Privileges to revoke.
            on: Database.table pattern.
            username: Username.
            host: Host (default: '%').

        Returns:
            Dictionary with revoke status.

        Example:
            >>> cm.revoke_privileges("INSERT", "mydb.*", "user", "localhost")
            {"status": "revoked", "privileges": "INSERT", ...}
        """
        conn = self.get_connection()
        conn.revoke_privileges(privileges, on, username, host)
        return {
            "status": "revoked",
            "privileges": privileges,
            "on": on,
            "from": f"{username}@{host}",
        }

    def show_grants(self, username: str, host: str = "%") -> list[str]:
        """Show grants for a user.

        Args:
            username: Username.
            host: Host (default: '%').

        Returns:
            List of grant statements.

        Example:
            >>> cm.show_grants("user", "localhost")
            ["GRANT SELECT ON *.* TO 'user'@'localhost'"]
        """
        conn = self.get_connection()
        return conn.show_grants(username, host)

    def server_status(self) -> dict[str, Any]:
        """Get server status information.

        Returns:
            Dictionary containing server metrics.

        Example:
            >>> cm.server_status()
            {"version": "8.0.30", "uptime": 3600, ...}
        """
        conn = self.get_connection()
        status = conn.server_status()
        return status.to_dict()

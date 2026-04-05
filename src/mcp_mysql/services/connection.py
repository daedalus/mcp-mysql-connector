from __future__ import annotations

from typing import Any

from mcp_mysql.adapters.mysql import ConnectionPool, MySQLConnection


class ConnectionManager:
    _instance: ConnectionManager | None = None

    def __new__(cls) -> ConnectionManager:
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
        if self._connection:
            self._connection.close()
            self._connection = None
        if self._pool:
            self._pool.close_all()
            self._pool = None
        return {"status": "disconnected"}

    @property
    def is_connected(self) -> bool:
        return self._connection is not None and self._connection.is_connected

    def get_connection(self) -> MySQLConnection:
        if not self._connection or not self._connection.is_connected:
            raise RuntimeError("Not connected to MySQL. Call connect() first.")
        return self._connection

    def execute(self, sql: str, params: tuple | dict | None = None) -> dict[str, Any]:
        conn = self.get_connection()
        result = conn.execute(sql, params)
        return result.to_dict()

    def commit(self) -> None:
        conn = self.get_connection()
        conn.commit()

    def rollback(self) -> None:
        conn = self.get_connection()
        conn.rollback()

    def list_databases(self) -> list[str]:
        conn = self.get_connection()
        return conn.list_databases()

    def list_tables(self, database: str | None = None) -> list[str]:
        conn = self.get_connection()
        return conn.list_tables(database)

    def describe_table(self, table: str, database: str | None = None) -> dict[str, Any]:
        conn = self.get_connection()
        schema = conn.describe_table(table, database)
        return schema.to_dict()

    def show_columns(
        self, table: str, database: str | None = None
    ) -> list[dict[str, Any]]:
        conn = self.get_connection()
        return conn.show_columns(table, database)

    def show_indexes(
        self, table: str, database: str | None = None
    ) -> list[dict[str, Any]]:
        conn = self.get_connection()
        return conn.show_indexes(table, database)

    def create_database(self, name: str, if_not_exists: bool = True) -> dict[str, Any]:
        conn = self.get_connection()
        conn.create_database(name, if_not_exists)
        return {"status": "created", "database": name}

    def drop_database(self, name: str, if_exists: bool = True) -> dict[str, Any]:
        conn = self.get_connection()
        conn.drop_database(name, if_exists)
        return {"status": "dropped", "database": name}

    def database_exists(self, name: str) -> bool:
        conn = self.get_connection()
        return conn.database_exists(name)

    def table_exists(self, table: str, database: str | None = None) -> bool:
        conn = self.get_connection()
        return conn.table_exists(table, database)

    def create_user(
        self, username: str, host: str = "%", password: str | None = None
    ) -> dict[str, Any]:
        conn = self.get_connection()
        conn.create_user(username, host, password)
        return {"status": "created", "user": f"{username}@{host}"}

    def drop_user(self, username: str, host: str = "%") -> dict[str, Any]:
        conn = self.get_connection()
        conn.drop_user(username, host)
        return {"status": "dropped", "user": f"{username}@{host}"}

    def grant_privileges(
        self, privileges: str, on: str, username: str, host: str = "%"
    ) -> dict[str, Any]:
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
        conn = self.get_connection()
        conn.revoke_privileges(privileges, on, username, host)
        return {
            "status": "revoked",
            "privileges": privileges,
            "on": on,
            "from": f"{username}@{host}",
        }

    def show_grants(self, username: str, host: str = "%") -> list[str]:
        conn = self.get_connection()
        return conn.show_grants(username, host)

    def server_status(self) -> dict[str, Any]:
        conn = self.get_connection()
        status = conn.server_status()
        return status.to_dict()

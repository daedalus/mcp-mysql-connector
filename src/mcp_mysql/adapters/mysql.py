from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING, Any

import pymysql
from pymysql.cursors import DictCursor

from mcp_mysql.core.models import ColumnInfo, QueryResult, ServerStatus, TableSchema

if TYPE_CHECKING:
    from collections.abc import Generator


class MySQLConnection:
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
        self.config = {
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
        self._connection = pymysql.connect(**self.config)

    def close(self) -> None:
        if self._connection:
            self._connection.close()
            self._connection = None

    @property
    def is_connected(self) -> bool:
        return self._connection is not None and self._connection.open

    @contextmanager
    def cursor(self) -> Generator[DictCursor, None, None]:
        if not self._connection:
            self.connect()
        cursor = self._connection.cursor()
        try:
            yield cursor
        finally:
            cursor.close()

    def execute(self, sql: str, params: tuple | dict | None = None) -> QueryResult:
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
        with self.cursor() as cur:
            cur.executemany(sql, params_list)
            return cur.rowcount

    def commit(self) -> None:
        if self._connection:
            self._connection.commit()

    def rollback(self) -> None:
        if self._connection:
            self._connection.rollback()

    def list_databases(self) -> list[str]:
        result = self.execute("SHOW DATABASES")
        return [row[0] for row in result.rows]

    def list_tables(self, database: str | None = None) -> list[str]:
        if database:
            self.execute(f"USE `{database}`")
        result = self.execute("SHOW TABLES")
        return [row[0] for row in result.rows]

    def describe_table(self, table: str, database: str | None = None) -> TableSchema:
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
        if if_not_exists:
            self.execute(f"CREATE DATABASE IF NOT EXISTS `{name}`")
        else:
            self.execute(f"CREATE DATABASE `{name}`")

    def drop_database(self, name: str, if_exists: bool = True) -> None:
        if if_exists:
            self.execute(f"DROP DATABASE IF EXISTS `{name}`")
        else:
            self.execute(f"DROP DATABASE `{name}`")

    def database_exists(self, name: str) -> bool:
        result = self.execute(
            "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = %s",
            (name,),
        )
        return len(result.rows) > 0

    def table_exists(self, table: str, database: str | None = None) -> bool:
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
        if password:
            self.execute(
                f"CREATE USER '{username}'@'{host}' IDENTIFIED BY %s", (password,)
            )
        else:
            self.execute(f"CREATE USER '{username}'@'{host}'")

    def drop_user(self, username: str, host: str = "%") -> None:
        self.execute(f"DROP USER '{username}'@'{host}'")

    def grant_privileges(
        self, privileges: str, on: str, username: str, host: str = "%"
    ) -> None:
        self.execute(f"GRANT {privileges} ON {on} TO '{username}'@'{host}'")
        self.execute("FLUSH PRIVILEGES")

    def revoke_privileges(
        self, privileges: str, on: str, username: str, host: str = "%"
    ) -> None:
        self.execute(f"REVOKE {privileges} ON {on} FROM '{username}'@'{host}'")
        self.execute("FLUSH PRIVILEGES")

    def show_grants(self, username: str, host: str = "%") -> list[str]:
        result = self.execute(f"SHOW GRANTS FOR '{username}'@'{host}'")
        return [row[0] for row in result.rows]

    def server_status(self) -> ServerStatus:
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
    def __init__(
        self,
        host: str = "localhost",
        port: int = 3306,
        user: str = "root",
        password: str = "",
        database: str = "",
        pool_size: int = 5,
    ) -> None:
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
        if len(self._pool) < self.pool_size:
            self._pool.append(conn)
        else:
            conn.close()

    def close_all(self) -> None:
        for conn in self._pool:
            conn.close()
        self._pool.clear()

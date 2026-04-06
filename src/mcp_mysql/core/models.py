"""Core data models for MCP MySQL server.

This module provides dataclasses for representing MySQL query results,
table schemas, column information, and server status.
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class QueryResult:
    """Represents the result of a SQL query execution.

    Attributes:
        columns: List of column names returned by the query.
        rows: List of rows, where each row is a list of values.
        affected_rows: Number of rows affected by the query (for INSERT, UPDATE, DELETE).
    """

    columns: list[str]
    rows: list[list[Any]]
    affected_rows: int

    def to_dict(self) -> dict[str, Any]:
        """Convert QueryResult to a dictionary.

        Returns:
            Dictionary representation with columns, rows, and affected_rows.
        """
        return {
            "columns": self.columns,
            "rows": self.rows,
            "affected_rows": self.affected_rows,
        }


@dataclass
class ColumnInfo:
    """Represents metadata about a table column.

    Attributes:
        name: Column name.
        type: SQL data type (e.g., 'int', 'varchar(255)').
        nullable: Whether the column allows NULL values.
        key: Key type ('PRI' for primary key, 'MUL' for index, etc.).
        default: Default value for the column.
        extra: Extra information (e.g., 'auto_increment').
    """

    name: str
    type: str
    nullable: bool
    key: str
    default: str | None
    extra: str | None


@dataclass
class TableSchema:
    """Represents the schema of a MySQL table.

    Attributes:
        name: Table name.
        columns: List of ColumnInfo objects describing each column.
    """

    name: str
    columns: list[ColumnInfo]

    def to_dict(self) -> dict[str, Any]:
        """Convert TableSchema to a dictionary.

        Returns:
            Dictionary representation with name and columns.
        """
        return {
            "name": self.name,
            "columns": [
                {
                    "name": c.name,
                    "type": c.type,
                    "nullable": c.nullable,
                    "key": c.key,
                    "default": c.default,
                    "extra": c.extra,
                }
                for c in self.columns
            ],
        }


@dataclass
class ServerStatus:
    """Represents MySQL server status information.

    Attributes:
        version: MySQL server version string.
        uptime: Server uptime in seconds.
        threads: Number of active threads.
        questions: Total number of queries executed.
        slow_queries: Number of slow queries.
        opens: Total number of tables opened.
        flush_tables: Number of FLUSH operations.
        open_tables: Number of currently open tables.
    """

    version: str
    uptime: int
    threads: int
    questions: int
    slow_queries: int
    opens: int
    flush_tables: int
    open_tables: int

    def to_dict(self) -> dict[str, Any]:
        """Convert ServerStatus to a dictionary.

        Returns:
            Dictionary with all server status fields.
        """
        return {
            "version": self.version,
            "uptime": self.uptime,
            "threads": self.threads,
            "questions": self.questions,
            "slow_queries": self.slow_queries,
            "opens": self.opens,
            "flush_tables": self.flush_tables,
            "open_tables": self.open_tables,
        }

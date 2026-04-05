from dataclasses import dataclass
from typing import Any


@dataclass
class QueryResult:
    columns: list[str]
    rows: list[list[Any]]
    affected_rows: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "columns": self.columns,
            "rows": self.rows,
            "affected_rows": self.affected_rows,
        }


@dataclass
class ColumnInfo:
    name: str
    type: str
    nullable: bool
    key: str
    default: str | None
    extra: str | None


@dataclass
class TableSchema:
    name: str
    columns: list[ColumnInfo]

    def to_dict(self) -> dict[str, Any]:
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
    version: str
    uptime: int
    threads: int
    questions: int
    slow_queries: int
    opens: int
    flush_tables: int
    open_tables: int

    def to_dict(self) -> dict[str, Any]:
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

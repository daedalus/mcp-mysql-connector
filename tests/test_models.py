from mcp_mysql_connector.core.models import (
    ColumnInfo,
    QueryResult,
    ServerStatus,
    TableSchema,
)


class TestQueryResult:
    def test_query_result_to_dict(self):
        result = QueryResult(
            columns=["id", "name"],
            rows=[[1, "Alice"], [2, "Bob"]],
            affected_rows=2,
        )
        expected = {
            "columns": ["id", "name"],
            "rows": [[1, "Alice"], [2, "Bob"]],
            "affected_rows": 2,
        }
        assert result.to_dict() == expected

    def test_query_result_empty(self):
        result = QueryResult(columns=[], rows=[], affected_rows=0)
        assert result.to_dict() == {
            "columns": [],
            "rows": [],
            "affected_rows": 0,
        }


class TestColumnInfo:
    def test_column_info_creation(self):
        col = ColumnInfo(
            name="id",
            type="int",
            nullable=False,
            key="PRI",
            default=None,
            extra="auto_increment",
        )
        assert col.name == "id"
        assert col.type == "int"
        assert col.nullable is False
        assert col.key == "PRI"

    def test_column_info_to_dict(self):
        col = ColumnInfo(
            name="id",
            type="int",
            nullable=False,
            key="PRI",
            default=None,
            extra="auto_increment",
        )
        d = {
            "name": "id",
            "type": "int",
            "nullable": False,
            "key": "PRI",
            "default": None,
            "extra": "auto_increment",
        }
        assert {
            "name": col.name,
            "type": col.type,
            "nullable": col.nullable,
            "key": col.key,
            "default": col.default,
            "extra": col.extra,
        } == d


class TestTableSchema:
    def test_table_schema_creation(self):
        cols = [
            ColumnInfo(
                name="id",
                type="int",
                nullable=False,
                key="PRI",
                default=None,
                extra="auto_increment",
            ),
            ColumnInfo(
                name="name",
                type="varchar(255)",
                nullable=True,
                key="",
                default=None,
                extra="",
            ),
        ]
        schema = TableSchema(name="users", columns=cols)
        assert schema.name == "users"
        assert len(schema.columns) == 2

    def test_table_schema_to_dict(self):
        cols = [
            ColumnInfo(
                name="id",
                type="int",
                nullable=False,
                key="PRI",
                default=None,
                extra="auto_increment",
            ),
        ]
        schema = TableSchema(name="users", columns=cols)
        d = schema.to_dict()
        assert d["name"] == "users"
        assert len(d["columns"]) == 1
        assert d["columns"][0]["name"] == "id"


class TestServerStatus:
    def test_server_status_creation(self):
        status = ServerStatus(
            version="8.0.30",
            uptime=3600,
            threads=2,
            questions=100,
            slow_queries=0,
            opens=50,
            flush_tables=10,
            open_tables=20,
        )
        assert status.version == "8.0.30"
        assert status.uptime == 3600

    def test_server_status_to_dict(self):
        status = ServerStatus(
            version="8.0.30",
            uptime=3600,
            threads=2,
            questions=100,
            slow_queries=0,
            opens=50,
            flush_tables=10,
            open_tables=20,
        )
        d = status.to_dict()
        assert d["version"] == "8.0.30"
        assert d["uptime"] == 3600
        assert d["threads"] == 2

from unittest.mock import MagicMock, patch

import pytest

from mcp_mysql.services.connection import ConnectionManager


class TestConnectionManager:
    def setup_method(self):
        ConnectionManager._instance = None

    @patch("mcp_mysql.services.connection.MySQLConnection")
    def test_connect(self, mock_conn_class):
        mock_conn = MagicMock()
        mock_conn.is_connected = True
        mock_conn_class.return_value = mock_conn

        cm = ConnectionManager()
        result = cm.connect(host="localhost", user="root", password="secret")

        assert result["status"] == "connected"
        mock_conn.connect.assert_called_once()

    @patch("mcp_mysql.services.connection.MySQLConnection")
    def test_connect_with_pool(self, mock_conn_class):
        mock_conn = MagicMock()
        mock_conn.is_connected = True
        mock_conn_class.return_value = mock_conn

        cm = ConnectionManager()
        cm.connect(host="localhost", use_pool=True, pool_size=10)

        assert cm._pool is not None

    @patch("mcp_mysql.services.connection.MySQLConnection")
    def test_disconnect(self, mock_conn_class):
        mock_conn = MagicMock()
        mock_conn_class.return_value = mock_conn

        cm = ConnectionManager()
        cm._connection = mock_conn
        result = cm.disconnect()

        assert result["status"] == "disconnected"
        mock_conn.close.assert_called_once()
        assert cm._connection is None

    def test_get_connection_not_connected(self):
        cm = ConnectionManager()
        cm._connection = None
        with pytest.raises(RuntimeError, match="Not connected"):
            cm.get_connection()

    @patch("mcp_mysql.services.connection.MySQLConnection")
    def test_get_connection(self, mock_conn_class):
        mock_conn = MagicMock()
        mock_conn.is_connected = True
        mock_conn_class.return_value = mock_conn

        cm = ConnectionManager()
        cm._connection = mock_conn
        conn = cm.get_connection()
        assert conn == mock_conn

    @patch("mcp_mysql.services.connection.MySQLConnection")
    def test_execute(self, mock_conn_class):
        mock_conn = MagicMock()
        mock_conn.is_connected = True
        mock_result = MagicMock()
        mock_result.to_dict.return_value = {"columns": ["id"], "rows": [[1]]}
        mock_conn.execute.return_value = mock_result
        mock_conn_class.return_value = mock_conn

        cm = ConnectionManager()
        cm._connection = mock_conn
        result = cm.execute("SELECT * FROM users")
        assert "columns" in result

    @patch("mcp_mysql.services.connection.MySQLConnection")
    def test_commit(self, mock_conn_class):
        mock_conn = MagicMock()
        mock_conn.is_connected = True
        mock_conn_class.return_value = mock_conn

        cm = ConnectionManager()
        cm._connection = mock_conn
        cm.commit()
        mock_conn.commit.assert_called_once()

    @patch("mcp_mysql.services.connection.MySQLConnection")
    def test_rollback(self, mock_conn_class):
        mock_conn = MagicMock()
        mock_conn.is_connected = True
        mock_conn_class.return_value = mock_conn

        cm = ConnectionManager()
        cm._connection = mock_conn
        cm.rollback()
        mock_conn.rollback.assert_called_once()

    @patch("mcp_mysql.services.connection.MySQLConnection")
    def test_list_databases(self, mock_conn_class):
        mock_conn = MagicMock()
        mock_conn.is_connected = True
        mock_conn.list_databases.return_value = ["mysql", "testdb"]
        mock_conn_class.return_value = mock_conn

        cm = ConnectionManager()
        cm._connection = mock_conn
        result = cm.list_databases()
        assert result == ["mysql", "testdb"]

    @patch("mcp_mysql.services.connection.MySQLConnection")
    def test_list_tables(self, mock_conn_class):
        mock_conn = MagicMock()
        mock_conn.is_connected = True
        mock_conn.list_tables.return_value = ["users", "orders"]
        mock_conn_class.return_value = mock_conn

        cm = ConnectionManager()
        cm._connection = mock_conn
        result = cm.list_tables("testdb")
        assert result == ["users", "orders"]

    @patch("mcp_mysql.services.connection.MySQLConnection")
    def test_describe_table(self, mock_conn_class):
        mock_conn = MagicMock()
        mock_conn.is_connected = True
        mock_schema = MagicMock()
        mock_schema.to_dict.return_value = {"name": "users", "columns": []}
        mock_conn.describe_table.return_value = mock_schema
        mock_conn_class.return_value = mock_conn

        cm = ConnectionManager()
        cm._connection = mock_conn
        result = cm.describe_table("users", "testdb")
        assert result["name"] == "users"

    @patch("mcp_mysql.services.connection.MySQLConnection")
    def test_show_columns(self, mock_conn_class):
        mock_conn = MagicMock()
        mock_conn.is_connected = True
        mock_conn.show_columns.return_value = [{"field": "id", "type": "int"}]
        mock_conn_class.return_value = mock_conn

        cm = ConnectionManager()
        cm._connection = mock_conn
        result = cm.show_columns("users", "testdb")
        assert len(result) == 1

    @patch("mcp_mysql.services.connection.MySQLConnection")
    def test_show_indexes(self, mock_conn_class):
        mock_conn = MagicMock()
        mock_conn.is_connected = True
        mock_conn.show_indexes.return_value = [{"key_name": "PRIMARY"}]
        mock_conn_class.return_value = mock_conn

        cm = ConnectionManager()
        cm._connection = mock_conn
        result = cm.show_indexes("users", "testdb")
        assert len(result) == 1

    @patch("mcp_mysql.services.connection.MySQLConnection")
    def test_create_database(self, mock_conn_class):
        mock_conn = MagicMock()
        mock_conn.is_connected = True
        mock_conn_class.return_value = mock_conn

        cm = ConnectionManager()
        cm._connection = mock_conn
        result = cm.create_database("newdb")
        assert result["status"] == "created"

    @patch("mcp_mysql.services.connection.MySQLConnection")
    def test_drop_database(self, mock_conn_class):
        mock_conn = MagicMock()
        mock_conn.is_connected = True
        mock_conn_class.return_value = mock_conn

        cm = ConnectionManager()
        cm._connection = mock_conn
        result = cm.drop_database("olddb")
        assert result["status"] == "dropped"

    @patch("mcp_mysql.services.connection.MySQLConnection")
    def test_database_exists_true(self, mock_conn_class):
        mock_conn = MagicMock()
        mock_conn.is_connected = True
        mock_conn.database_exists.return_value = True
        mock_conn_class.return_value = mock_conn

        cm = ConnectionManager()
        cm._connection = mock_conn
        assert cm.database_exists("testdb") is True

    @patch("mcp_mysql.services.connection.MySQLConnection")
    def test_database_exists_false(self, mock_conn_class):
        mock_conn = MagicMock()
        mock_conn.is_connected = True
        mock_conn.database_exists.return_value = False
        mock_conn_class.return_value = mock_conn

        cm = ConnectionManager()
        cm._connection = mock_conn
        assert cm.database_exists("nonexistent") is False

    @patch("mcp_mysql.services.connection.MySQLConnection")
    def test_table_exists_true(self, mock_conn_class):
        mock_conn = MagicMock()
        mock_conn.is_connected = True
        mock_conn.table_exists.return_value = True
        mock_conn_class.return_value = mock_conn

        cm = ConnectionManager()
        cm._connection = mock_conn
        assert cm.table_exists("users", "testdb") is True

    @patch("mcp_mysql.services.connection.MySQLConnection")
    def test_table_exists_false(self, mock_conn_class):
        mock_conn = MagicMock()
        mock_conn.is_connected = True
        mock_conn.table_exists.return_value = False
        mock_conn_class.return_value = mock_conn

        cm = ConnectionManager()
        cm._connection = mock_conn
        assert cm.table_exists("nonexistent", "testdb") is False

    @patch("mcp_mysql.services.connection.MySQLConnection")
    def test_create_user(self, mock_conn_class):
        mock_conn = MagicMock()
        mock_conn.is_connected = True
        mock_conn_class.return_value = mock_conn

        cm = ConnectionManager()
        cm._connection = mock_conn
        result = cm.create_user("newuser", "localhost", "password")
        assert result["status"] == "created"

    @patch("mcp_mysql.services.connection.MySQLConnection")
    def test_drop_user(self, mock_conn_class):
        mock_conn = MagicMock()
        mock_conn.is_connected = True
        mock_conn_class.return_value = mock_conn

        cm = ConnectionManager()
        cm._connection = mock_conn
        result = cm.drop_user("olduser", "localhost")
        assert result["status"] == "dropped"

    @patch("mcp_mysql.services.connection.MySQLConnection")
    def test_grant_privileges(self, mock_conn_class):
        mock_conn = MagicMock()
        mock_conn.is_connected = True
        mock_conn_class.return_value = mock_conn

        cm = ConnectionManager()
        cm._connection = mock_conn
        result = cm.grant_privileges("SELECT", "testdb.*", "user", "localhost")
        assert result["status"] == "granted"

    @patch("mcp_mysql.services.connection.MySQLConnection")
    def test_revoke_privileges(self, mock_conn_class):
        mock_conn = MagicMock()
        mock_conn.is_connected = True
        mock_conn_class.return_value = mock_conn

        cm = ConnectionManager()
        cm._connection = mock_conn
        result = cm.revoke_privileges("SELECT", "testdb.*", "user", "localhost")
        assert result["status"] == "revoked"

    @patch("mcp_mysql.services.connection.MySQLConnection")
    def test_show_grants(self, mock_conn_class):
        mock_conn = MagicMock()
        mock_conn.is_connected = True
        mock_conn.show_grants.return_value = [
            "GRANT SELECT ON *.* TO 'user'@'localhost'"
        ]
        mock_conn_class.return_value = mock_conn

        cm = ConnectionManager()
        cm._connection = mock_conn
        result = cm.show_grants("user", "localhost")
        assert len(result) == 1

    @patch("mcp_mysql.services.connection.MySQLConnection")
    def test_server_status(self, mock_conn_class):
        mock_conn = MagicMock()
        mock_conn.is_connected = True
        mock_status = MagicMock()
        mock_status.to_dict.return_value = {"version": "8.0.30", "uptime": 3600}
        mock_conn.server_status.return_value = mock_status
        mock_conn_class.return_value = mock_conn

        cm = ConnectionManager()
        cm._connection = mock_conn
        result = cm.server_status()
        assert result["version"] == "8.0.30"

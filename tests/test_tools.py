from unittest.mock import MagicMock, patch

from mcp_mysql.tools import mysql_tools


class TestConnect:
    @patch("mcp_mysql.tools.mysql_tools.get_connection_manager")
    def test_connect_success(self, mock_get_cm):
        mock_cm = MagicMock()
        mock_cm.connect.return_value = {
            "status": "connected",
            "host": "localhost",
            "port": 3306,
            "database": "testdb",
        }
        mock_get_cm.return_value = mock_cm

        result = mysql_tools.connect(
            host="localhost",
            user="root",
            password="secret",
            database="testdb",
        )

        assert result["status"] == "connected"
        mock_cm.connect.assert_called_once()

    @patch("mcp_mysql.tools.mysql_tools.get_connection_manager")
    def test_connect_with_pool(self, mock_get_cm):
        mock_cm = MagicMock()
        mock_cm.connect.return_value = {"status": "connected"}
        mock_get_cm.return_value = mock_cm

        result = mysql_tools.connect(host="localhost", use_pool=True, pool_size=10)

        mock_cm.connect.assert_called_once()
        call_kwargs = mock_cm.connect.call_args[1]
        assert call_kwargs["use_pool"] is True
        assert call_kwargs["pool_size"] == 10


class TestDisconnect:
    @patch("mcp_mysql.tools.mysql_tools.get_connection_manager")
    def test_disconnect(self, mock_get_cm):
        mock_cm = MagicMock()
        mock_cm.disconnect.return_value = {"status": "disconnected"}
        mock_get_cm.return_value = mock_cm

        result = mysql_tools.disconnect()

        assert result["status"] == "disconnected"
        mock_cm.disconnect.assert_called_once()


class TestExecuteQuery:
    @patch("mcp_mysql.tools.mysql_tools.get_connection_manager")
    def test_execute_query(self, mock_get_cm):
        mock_cm = MagicMock()
        mock_cm.execute.return_value = {
            "columns": ["id", "name"],
            "rows": [[1, "Alice"]],
            "affected_rows": 1,
        }
        mock_get_cm.return_value = mock_cm

        result = mysql_tools.execute_query("SELECT * FROM users")

        assert result["columns"] == ["id", "name"]
        assert result["rows"] == [[1, "Alice"]]
        mock_cm.execute.assert_called_once_with("SELECT * FROM users", None)


class TestListDatabases:
    @patch("mcp_mysql.tools.mysql_tools.get_connection_manager")
    def test_list_databases(self, mock_get_cm):
        mock_cm = MagicMock()
        mock_cm.list_databases.return_value = ["mysql", "testdb", "information_schema"]
        mock_get_cm.return_value = mock_cm

        result = mysql_tools.list_databases()

        assert result == ["mysql", "testdb", "information_schema"]
        mock_cm.list_databases.assert_called_once()


class TestListTables:
    @patch("mcp_mysql.tools.mysql_tools.get_connection_manager")
    def test_list_tables(self, mock_get_cm):
        mock_cm = MagicMock()
        mock_cm.list_tables.return_value = ["users", "orders", "products"]
        mock_get_cm.return_value = mock_cm

        result = mysql_tools.list_tables("testdb")

        assert result == ["users", "orders", "products"]
        mock_cm.list_tables.assert_called_once_with("testdb")

    @patch("mcp_mysql.tools.mysql_tools.get_connection_manager")
    def test_list_tables_no_database(self, mock_get_cm):
        mock_cm = MagicMock()
        mock_cm.list_tables.return_value = ["users", "orders"]
        mock_get_cm.return_value = mock_cm

        result = mysql_tools.list_tables()

        assert result == ["users", "orders"]
        mock_cm.list_tables.assert_called_once_with(None)


class TestDescribeTable:
    @patch("mcp_mysql.tools.mysql_tools.get_connection_manager")
    def test_describe_table(self, mock_get_cm):
        mock_cm = MagicMock()
        mock_cm.describe_table.return_value = {
            "name": "users",
            "columns": [
                {
                    "name": "id",
                    "type": "int",
                    "nullable": False,
                    "key": "PRI",
                    "default": None,
                    "extra": "auto_increment",
                }
            ],
        }
        mock_get_cm.return_value = mock_cm

        result = mysql_tools.describe_table("users", "testdb")

        assert result["name"] == "users"
        assert len(result["columns"]) == 1
        mock_cm.describe_table.assert_called_once_with("users", "testdb")


class TestCreateDatabase:
    @patch("mcp_mysql.tools.mysql_tools.get_connection_manager")
    def test_create_database(self, mock_get_cm):
        mock_cm = MagicMock()
        mock_cm.create_database.return_value = {
            "status": "created",
            "database": "newdb",
        }
        mock_get_cm.return_value = mock_cm

        result = mysql_tools.create_database("newdb")

        assert result["status"] == "created"
        assert result["database"] == "newdb"
        mock_cm.create_database.assert_called_once_with("newdb", True)


class TestDropDatabase:
    @patch("mcp_mysql.tools.mysql_tools.get_connection_manager")
    def test_drop_database(self, mock_get_cm):
        mock_cm = MagicMock()
        mock_cm.drop_database.return_value = {"status": "dropped", "database": "olddb"}
        mock_get_cm.return_value = mock_cm

        result = mysql_tools.drop_database("olddb")

        assert result["status"] == "dropped"
        mock_cm.drop_database.assert_called_once_with("olddb", True)


class TestTableExists:
    @patch("mcp_mysql.tools.mysql_tools.get_connection_manager")
    def test_table_exists_true(self, mock_get_cm):
        mock_cm = MagicMock()
        mock_cm.table_exists.return_value = True
        mock_get_cm.return_value = mock_cm

        result = mysql_tools.table_exists("users", "testdb")

        assert result is True
        mock_cm.table_exists.assert_called_once_with("users", "testdb")

    @patch("mcp_mysql.tools.mysql_tools.get_connection_manager")
    def test_table_exists_false(self, mock_get_cm):
        mock_cm = MagicMock()
        mock_cm.table_exists.return_value = False
        mock_get_cm.return_value = mock_cm

        result = mysql_tools.table_exists("nonexistent", "testdb")

        assert result is False


class TestDatabaseExists:
    @patch("mcp_mysql.tools.mysql_tools.get_connection_manager")
    def test_database_exists_true(self, mock_get_cm):
        mock_cm = MagicMock()
        mock_cm.database_exists.return_value = True
        mock_get_cm.return_value = mock_cm

        result = mysql_tools.database_exists("testdb")

        assert result is True
        mock_cm.database_exists.assert_called_once_with("testdb")


class TestServerStatus:
    @patch("mcp_mysql.tools.mysql_tools.get_connection_manager")
    def test_server_status(self, mock_get_cm):
        mock_cm = MagicMock()
        mock_cm.server_status.return_value = {
            "version": "8.0.30",
            "uptime": 3600,
            "threads": 2,
            "questions": 100,
            "slow_queries": 0,
            "opens": 50,
            "flush_tables": 10,
            "open_tables": 20,
        }
        mock_get_cm.return_value = mock_cm

        result = mysql_tools.server_status()

        assert result["version"] == "8.0.30"
        assert result["uptime"] == 3600
        mock_cm.server_status.assert_called_once()


class TestTransaction:
    @patch("mcp_mysql.tools.mysql_tools.get_connection_manager")
    def test_commit(self, mock_get_cm):
        mock_cm = MagicMock()
        mock_get_cm.return_value = mock_cm

        result = mysql_tools.commit()

        assert result["status"] == "committed"
        mock_cm.commit.assert_called_once()

    @patch("mcp_mysql.tools.mysql_tools.get_connection_manager")
    def test_rollback(self, mock_get_cm):
        mock_cm = MagicMock()
        mock_get_cm.return_value = mock_cm

        result = mysql_tools.rollback()

        assert result["status"] == "rolledback"
        mock_cm.rollback.assert_called_once()


class TestIsConnected:
    @patch("mcp_mysql.tools.mysql_tools.get_connection_manager")
    def test_is_connected_true(self, mock_get_cm):
        mock_cm = MagicMock()
        mock_cm.is_connected = True
        mock_get_cm.return_value = mock_cm

        result = mysql_tools.is_connected()

        assert result is True

    @patch("mcp_mysql.tools.mysql_tools.get_connection_manager")
    def test_is_connected_false(self, mock_get_cm):
        mock_cm = MagicMock()
        mock_cm.is_connected = False
        mock_get_cm.return_value = mock_cm

        result = mysql_tools.is_connected()

        assert result is False

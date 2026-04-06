from unittest.mock import MagicMock, patch

from mcp_mysql.adapters.mysql import ConnectionPool, MySQLConnection


class TestMySQLConnection:
    def test_init_with_defaults(self):
        conn = MySQLConnection()
        assert conn.config["host"] == "localhost"
        assert conn.config["port"] == 3306
        assert conn.config["user"] == "root"

    def test_init_with_custom_params(self):
        conn = MySQLConnection(
            host="remotehost",
            port=3307,
            user="admin",
            password="secret",
            database="testdb",
        )
        assert conn.config["host"] == "remotehost"
        assert conn.config["port"] == 3307
        assert conn.config["user"] == "admin"
        assert conn.config["password"] == "secret"
        assert conn.config["database"] == "testdb"

    @patch("mcp_mysql.adapters.mysql.pymysql.connect")
    def test_connect(self, mock_connect):
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        conn = MySQLConnection()
        conn.connect()
        mock_connect.assert_called_once()
        assert conn._connection == mock_conn

    def test_close(self):
        mock_conn = MagicMock()
        conn = MySQLConnection()
        conn._connection = mock_conn
        conn.close()
        mock_conn.close.assert_called_once()
        assert conn._connection is None

    def test_is_connected_false_when_none(self):
        conn = MySQLConnection()
        assert conn.is_connected is False

    @patch("mcp_mysql.adapters.mysql.pymysql.connect")
    def test_is_connected_true_when_open(self, mock_connect):
        mock_conn = MagicMock()
        mock_conn.open = True
        mock_connect.return_value = mock_conn
        conn = MySQLConnection()
        conn.connect()
        assert conn.is_connected is True


class TestConnectionPool:
    def test_init(self):
        pool = ConnectionPool(host="localhost", user="root", pool_size=3)
        assert pool.pool_size == 3
        assert pool.config["host"] == "localhost"

    @patch("mcp_mysql.adapters.mysql.MySQLConnection")
    def test_get_connection(self, mock_conn_class):
        mock_conn = MagicMock()
        mock_conn.is_connected = False
        mock_conn_class.return_value = mock_conn

        pool = ConnectionPool(pool_size=3)
        conn = pool.get_connection()
        assert conn == mock_conn
        mock_conn.connect.assert_called_once()

    def test_return_connection(self):
        pool = ConnectionPool(pool_size=3)
        mock_conn = MagicMock()
        pool.return_connection(mock_conn)
        assert len(pool._pool) == 1

    def test_close_all(self):
        pool = ConnectionPool(pool_size=3)
        mock_conn = MagicMock()
        pool._pool.append(mock_conn)
        pool.close_all()
        mock_conn.close.assert_called_once()
        assert len(pool._pool) == 0

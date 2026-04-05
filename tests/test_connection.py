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
        result = cm.connect(host="localhost", use_pool=True, pool_size=10)

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

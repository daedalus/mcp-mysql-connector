import pytest


@pytest.fixture
def mock_mysql_connection():
    from unittest.mock import MagicMock

    conn = MagicMock()
    conn.is_connected = True
    return conn

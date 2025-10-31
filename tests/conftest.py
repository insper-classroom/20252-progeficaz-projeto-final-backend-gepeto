import pytest
import sys
import os
from unittest.mock import MagicMock, patch


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from servidor import app as flask_app


@pytest.fixture(autouse=True)
def mock_db(monkeypatch):
    """Mocka a conexão com MongoDB para todos os testes"""
    # Usa monkeypatch que funciona melhor para mockar antes de execução
    mock_connect = MagicMock(return_value=None)
    monkeypatch.setattr('utils.connect_db', mock_connect)
    return mock_connect


@pytest.fixture()
def app():
    flask_app.config.update(TESTING=True)
    yield flask_app


@pytest.fixture()
def client(app):
    return app.test_client()
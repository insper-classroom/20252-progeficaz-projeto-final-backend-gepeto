import pytest
import sys
import os


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from servidor import app as flask_app


@pytest.fixture()
def app():
    flask_app.config.update(TESTING=True)
    yield flask_app


@pytest.fixture()
def client(app):
    return app.test_client()
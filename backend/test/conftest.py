import pytest

from .setup import engine
from backend.sql.db import SqlDatabase
from backend.nosql.db import MongoDatabase


@pytest.fixture(autouse=True)
def reset_db(request):
    SqlDatabase.reset(engine)


@pytest.fixture(autouse=True)
def rest_mongo_db(request):
    if 'not integration' not in request.session.config.option.keyword:
        MongoDatabase.reset(MongoDatabase.database())


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "integration(name): mark test to run only in integration"
    )

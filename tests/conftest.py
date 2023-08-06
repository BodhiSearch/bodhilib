import os

import dotenv
import pytest

dotenv.load_dotenv(".env.test")


def pytest_sessionstart(session):
    for key, value in os.environ.items():
        session.config.cache.set(key, value)


def pytest_collection_modifyitems(config, items):
    for item in items:
        item.add_marker(pytest.mark.all)

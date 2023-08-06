import dotenv
import os

dotenv.load_dotenv(".env.test")


def pytest_sessionstart(session):
    for key, value in os.environ.items():
        session.config.cache.set(key, value)

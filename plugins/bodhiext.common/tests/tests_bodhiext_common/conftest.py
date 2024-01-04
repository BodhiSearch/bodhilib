import os
from pathlib import Path
import pytest

CURRENT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
TEST_DATA_DIR = (CURRENT_DIR / "test_data").resolve()


def pytest_collection_modifyitems(config, items):
  for item in items:
    item.add_marker(pytest.mark.all)

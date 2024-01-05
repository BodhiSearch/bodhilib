import os
import shutil
from pathlib import Path

current_dir = Path(os.path.abspath(os.path.dirname(__file__)))
tmp_dir = current_dir / ".." / "tmp"


def setup_file_loader() -> None:
  os.makedirs(tmp_dir / "file_loader", exist_ok=True)
  with open(tmp_dir / "file_loader" / "test1.txt", "w") as f:
    f.write("hello world!")
  with open(tmp_dir / "file_loader" / "test2.txt", "w") as f:
    f.write("world hello!")


def teardown_file_loader() -> None:
  shutil.rmtree(tmp_dir / "file_loader")

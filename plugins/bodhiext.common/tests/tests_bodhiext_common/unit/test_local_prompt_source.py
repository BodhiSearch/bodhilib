import tempfile

import pytest
from bodhiext.prompt_source import LocalPromptSource

from tests_bodhiext_common.conftest import TEST_DATA_DIR

simple_templates_yaml = TEST_DATA_DIR / "prompt-sources" / "simple-templates.yaml"


@pytest.mark.parametrize(
  ["dir_path", "expected_error"],
  [
    ("missing", "Directory does not exists: dir='{dir_path}'"),
    (tempfile.NamedTemporaryFile(mode="w", delete=False).name, "Path is not a directory: dir='{dir_path}'"),
  ],
)
def test_local_prompt_source_raises_error_if_dir_missing_or_not_dir(dir_path, expected_error):
  with pytest.raises(ValueError) as e:
    _ = LocalPromptSource(dir=dir_path)
  assert str(e.value) == expected_error.format(dir_path=dir_path)


@pytest.mark.parametrize(
  ["files", "expected_error"],
  [
    (
      ["missing", simple_templates_yaml],
      "File does not exists: missing_files={files}",
    ),
    (
      [TEST_DATA_DIR / "prompt-sources", simple_templates_yaml],
      "Path is not a file: not_files={files}",
    ),
    (
      [TEST_DATA_DIR / "prompt-sources" / "not-yaml.txt", simple_templates_yaml],
      "File is not in yaml format: not_yaml={files}",
    ),
  ],
)
def test_local_prompt_source_raises_error_if_any_of_files_missing_or_not_yaml(files, expected_error):
  with pytest.raises(ValueError) as e:
    _ = LocalPromptSource(files=files)
  assert str(e.value) == expected_error.format(files=[str(files[0])])


def test_local_prompt_source_raise_error_if_files_not_list():
  files = str(simple_templates_yaml)
  with pytest.raises(ValueError) as e:
    _ = LocalPromptSource(files=files)
  assert str(e.value) == f"files should be a list of file paths: files='{files}'"


@pytest.mark.parametrize(
  "file, expected_error",
  [
    ("missing", "File does not exists: missing_files=['{file}']"),
    (TEST_DATA_DIR / "prompt-sources", "Path is not a file: not_files=['{file}']"),
    (TEST_DATA_DIR / "prompt-sources" / "not-yaml.txt", "File is not in yaml format: not_yaml=['{file}']"),
  ],
)
def test_local_prompt_source_raises_error_if_file_missing_or_not_yaml(file, expected_error):
  with pytest.raises(ValueError) as e:
    _ = LocalPromptSource(file=file)
  assert str(e.value) == expected_error.format(file=file)


@pytest.mark.parametrize("dir_path", [(str(TEST_DATA_DIR / "prompt-sources")), (TEST_DATA_DIR / "prompt-sources")])
def test_local_prompt_source_loads_from_given_dir_str_or_path(dir_path):
  sources = LocalPromptSource(dir=dir_path)
  assert len(sources.list_all()) == 3


@pytest.mark.parametrize(
  "files",
  [
    ([str(simple_templates_yaml)]),
    ([simple_templates_yaml]),
  ],
)
def test_local_prompt_source_loads_from_given_files_path_or_str(files):
  sources = LocalPromptSource(files=files)
  assert len(sources.list_all()) == 3


@pytest.mark.parametrize(
  "file",
  [
    (str(simple_templates_yaml)),
    (simple_templates_yaml),
  ],
)
def test_local_prompt_source_loads_from_given_file_path_or_str(file):
  sources = LocalPromptSource(file=file)
  assert len(sources.list_all()) == 3


def test_local_prompt_source_loads_from_given_files():
  files = [
    str(simple_templates_yaml),
    str(TEST_DATA_DIR / "prompt-templates" / "multiple-templates.yaml"),
  ]
  sources = LocalPromptSource(files=files)
  assert len(sources.list_all()) == 5


def test_local_prompt_loads_from_default_pkg_resource():
  sources = LocalPromptSource()
  assert len(sources.list_all()) == 2


def test_local_prompt_source_returns_tagged_template():
  sources = LocalPromptSource(dir=str(TEST_DATA_DIR / "prompt-sources"))
  result = sources.find({"tags": {"$in": ["funny"]}})
  assert len(result) == 2
  assert result[0].metadata == {"tags": ["funny", "simple"], "format": "jinja2", "id": "2"}
  assert result[1].metadata == {"tags": ["funny"], "format": "fstring", "id": "3"}


def test_local_prompt_source_returns_template_with_any_tags():
  sources = LocalPromptSource(dir=str(TEST_DATA_DIR / "prompt-sources"))
  result = sources.find({"tags": {"$in": ["education", "simple"]}})
  assert len(result) == 2
  assert result[0].metadata == {"tags": ["education", "simple"], "format": "fstring", "id": "1"}
  assert result[1].metadata == {"tags": ["funny", "simple"], "format": "jinja2", "id": "2"}


def test_local_prompt_source_returns_template_with_all_tags():
  sources = LocalPromptSource(dir=str(TEST_DATA_DIR / "prompt-sources"))
  result = sources.find({"tags": {"$all": ["simple", "funny"]}})
  assert len(result) == 1
  assert result[0].metadata == {"tags": ["funny", "simple"], "format": "jinja2", "id": "2"}


def test_local_prompt_source_returns_template_with_tag_not_matching():
  sources = LocalPromptSource(dir=str(TEST_DATA_DIR / "prompt-sources"))
  result = sources.find({"tags": {"$nin": ["simple", "education"]}})
  assert len(result) == 1
  assert result[0].metadata == {"tags": ["funny"], "format": "fstring", "id": "3"}


def test_local_prompt_source_returns_template_with_given_id():
  sources = LocalPromptSource(dir=str(TEST_DATA_DIR / "prompt-sources"))
  result = sources.find_by_id("2")
  assert result is not None
  assert result.metadata == {"tags": ["funny", "simple"], "format": "jinja2", "id": "2"}


def test_local_prompt_soruce_list_all():
  sources = LocalPromptSource(dir=str(TEST_DATA_DIR / "prompt-sources"))
  result = sources.list_all()
  assert len(result) == 3
  assert result[0].metadata["id"] == "1"
  assert result[1].metadata["id"] == "2"
  assert result[2].metadata["id"] == "3"

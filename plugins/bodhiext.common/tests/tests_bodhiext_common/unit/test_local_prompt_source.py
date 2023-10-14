import tempfile

import pytest
from bodhiext.prompt_source import LocalPromptSource

from tests_bodhiext_common.conftest import TEST_DATA_DIR


def test_local_prompt_source_raise_error_if_dir_missing():
    with pytest.raises(ValueError) as e:
        _ = LocalPromptSource(dir="missing")
    assert str(e.value) == "Directory does not exists: dir='missing'"


def test_local_prompt_source_raise_error_if_not_dir(tmp_path):
    with pytest.raises(ValueError) as e:
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            _ = LocalPromptSource(dir=f.name)
    assert str(e.value) == f"Path is not a directory: dir='{f.name}'"


def test_local_prompt_source_loads_from_given_dir():
    sources = LocalPromptSource(dir=str(TEST_DATA_DIR / "prompt-sources"))
    assert len(sources.list_all()) == 3


def test_local_prompt_source_loads_from_given_dir_path():
    sources = LocalPromptSource(dir=TEST_DATA_DIR / "prompt-sources")
    assert len(sources.list_all()) == 3


def test_local_prompt_source_loads_from_given_file():
    sources = LocalPromptSource(files=str(TEST_DATA_DIR / "prompt-sources" / "simple-templates.yaml"))
    assert len(sources.list_all()) == 3


def test_local_prompt_source_loads_from_given_file_path():
    sources = LocalPromptSource(files=TEST_DATA_DIR / "prompt-sources" / "simple-templates.yaml")
    assert len(sources.list_all()) == 3


def test_local_prompt_source_loads_from_given_files():
    files = [
        str(TEST_DATA_DIR / "prompt-sources" / "simple-templates.yaml"),
        str(TEST_DATA_DIR / "prompt-templates" / "multiple-templates.yaml"),
    ]
    sources = LocalPromptSource(files=files)
    assert len(sources.list_all()) == 5


def test_local_prompt_source_raises_error_if_file_missing():
    with pytest.raises(ValueError) as e:
        _ = LocalPromptSource(files=["missing"])
    assert str(e.value) == "File does not exists: missing_files=['missing']"


def test_local_prompt_source_raises_error_if_dir_passed():
    with pytest.raises(ValueError) as e:
        dir = str(TEST_DATA_DIR / "prompt-sources")
        _ = LocalPromptSource(files=[dir])
    assert str(e.value) == f"Path is not a file: not_files=['{dir}']"


def test_local_prompt_source_raises_error_if_not_yaml():
    with pytest.raises(ValueError) as e:
        not_yaml = str(TEST_DATA_DIR / "prompt-sources" / "not-yaml.txt")
        _ = LocalPromptSource(files=[not_yaml])
    assert str(e.value) == f"File is not in yaml format: not_yaml=['{not_yaml}']"


def test_local_prompt_loads_from_default_pkg_resource():
    sources = LocalPromptSource()
    assert len(sources.list_all()) == 1


def test_local_prompt_source_returns_tagged_template():
    sources = LocalPromptSource(dir=str(TEST_DATA_DIR / "prompt-sources"))
    result = sources.find({"tags": {"$in": ["funny"]}})
    assert len(result) == 2
    assert result[0].metadata == {"tags": ["funny", "simple"], "format": "jinja2", "id": 2}
    assert result[1].metadata == {"tags": ["funny"], "format": "fstring", "id": 3}


def test_local_prompt_source_returns_template_with_any_tags():
    sources = LocalPromptSource(dir=str(TEST_DATA_DIR / "prompt-sources"))
    result = sources.find({"tags": {"$in": ["education", "simple"]}})
    assert len(result) == 2
    assert result[0].metadata == {"tags": ["education", "simple"], "format": "fstring", "id": 1}
    assert result[1].metadata == {"tags": ["funny", "simple"], "format": "jinja2", "id": 2}


def test_local_prompt_source_returns_template_with_all_tags():
    sources = LocalPromptSource(dir=str(TEST_DATA_DIR / "prompt-sources"))
    result = sources.find({"tags": {"$all": ["simple", "funny"]}})
    assert len(result) == 1
    assert result[0].metadata == {"tags": ["funny", "simple"], "format": "jinja2", "id": 2}


def test_local_prompt_source_returns_template_with_tag_not_matching():
    sources = LocalPromptSource(dir=str(TEST_DATA_DIR / "prompt-sources"))
    result = sources.find({"tags": {"$nin": ["simple", "education"]}})
    assert len(result) == 1
    assert result[0].metadata == {"tags": ["funny"], "format": "fstring", "id": 3}


def test_local_prompt_soruce_list_all():
    sources = LocalPromptSource(dir=str(TEST_DATA_DIR / "prompt-sources"))
    result = sources.list_all()
    assert len(result) == 3
    assert result[0].metadata["id"] == 1
    assert result[1].metadata["id"] == 2
    assert result[2].metadata["id"] == 3

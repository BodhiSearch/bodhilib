from bodhiext.prompt_source import LocalDirectoryPromptSource

from tests_bodhiext_common.conftest import TEST_DATA_DIR


def test_bodhi_prompt_source_returns_tagged_template():
    sources = LocalDirectoryPromptSource(source_dir=str(TEST_DATA_DIR / "prompt-sources"))
    result = sources.find({"tags": {"$in": ["funny"]}})
    assert len(result) == 2
    assert result[0].metadata == {"tags": ["funny", "simple"], "format": "jinja2", "id": 2}
    assert result[1].metadata == {"tags": ["funny"], "format": "fstring", "id": 3}


def test_bodhi_prompt_source_returns_template_with_any_tags():
    sources = LocalDirectoryPromptSource(source_dir=str(TEST_DATA_DIR / "prompt-sources"))
    result = sources.find({"tags": {"$in": ["education", "simple"]}})
    assert len(result) == 2
    assert result[0].metadata == {"tags": ["education", "simple"], "format": "fstring", "id": 1}
    assert result[1].metadata == {"tags": ["funny", "simple"], "format": "jinja2", "id": 2}


def test_bodhi_prompt_source_returns_template_with_all_tags():
    sources = LocalDirectoryPromptSource(source_dir=str(TEST_DATA_DIR / "prompt-sources"))
    result = sources.find({"tags": {"$all": ["simple", "funny"]}})
    assert len(result) == 1
    assert result[0].metadata == {"tags": ["funny", "simple"], "format": "jinja2", "id": 2}

def test_bodhi_prompt_source_returns_template_with_tag_not_matching():
    sources = LocalDirectoryPromptSource(source_dir=str(TEST_DATA_DIR / "prompt-sources"))
    result = sources.find({"tags": {"$nin": ["simple", "education"]}})
    assert len(result) == 1
    assert result[0].metadata == {"tags": ["funny"], "format": "fstring", "id": 3}


def test_bodhi_prompt_soruce_list_all():
    sources = LocalDirectoryPromptSource(source_dir=str(TEST_DATA_DIR / "prompt-sources"))
    result = sources.list_all()
    assert len(result) == 3
    assert result[0].metadata["id"] == 1
    assert result[1].metadata["id"] == 2
    assert result[2].metadata["id"] == 3

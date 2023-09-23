import os
from pathlib import Path

import pytest
from bodhilib import Document, get_splitter

from tests_bodhitest.all_data import bodhiext_splitters

current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
test_data_dir = (current_dir / ".." / ".." / "test_data").resolve()


@pytest.fixture
def splitter_service(request):
    service_name = bodhiext_splitters[request.param]["service_name"]
    service_class = bodhiext_splitters[request.param]["service_class"]
    service_args = bodhiext_splitters[request.param]["service_args"]
    return get_splitter(service_name, oftype=service_class, **service_args)


@pytest.mark.live
@pytest.mark.parametrize("splitter_service", bodhiext_splitters.keys(), indirect=True)
def test_all_splitters_live_preserves_content(splitter_service):
    docs = []
    orig_text = ""
    for file in ["pg-great-work.txt", "pg-new-ideas.txt"]:
        with open(test_data_dir / file, "r", encoding="utf-8") as f:
            text = f.read()
            orig_text += text
            doc = Document(text=text, metadata={"filename": file})
            docs.append(doc)
    nodes = splitter_service.split(docs)
    node_text = "".join([node.text for node in nodes])
    assert node_text == orig_text

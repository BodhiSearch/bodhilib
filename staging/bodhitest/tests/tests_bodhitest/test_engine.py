from pathlib import Path

import pytest
from bodhiext.engine import DefaultSemanticEngine
from bodhilib import get_data_loader, get_embedder, get_llm, get_splitter, get_vector_db


@pytest.fixture
def llm():
  return get_llm(service_name="openai_chat", model="gpt-3.5-turbo")


@pytest.fixture
def file_loader():
  return get_data_loader(service_name="file")


@pytest.fixture
def embedder():
  return get_embedder(service_name="sentence_transformers")


@pytest.fixture
def splitter():
  return get_splitter(service_name="text_splitter", max_len=256, min_len=128, overlap=16)


@pytest.fixture
def vector_db():
  return get_vector_db(service_name="qdrant", host="localhost", port=6333)


@pytest.fixture
def engine(llm, file_loader, embedder, splitter, vector_db):
  return DefaultSemanticEngine(
    data_loader=file_loader,
    splitter=splitter,
    embedder=embedder,
    vector_db=vector_db,
    llm=llm,
    collection_name="test_collection",
  )


@pytest.fixture
def test_file():
  return str(Path(__file__).parent / "test_data" / "paul_graham_essay.txt")


@pytest.mark.live
def test_engine_rag(engine, test_file):
  engine.delete_collection()
  engine.create_collection()
  engine.add_resource(file=str(test_file))
  engine.ingest()
  response = engine.rag("What are authors thought about painting?")
  print(response)
  assert "painting" in response.text

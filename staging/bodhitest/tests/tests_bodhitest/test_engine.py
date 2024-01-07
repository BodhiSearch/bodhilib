from pathlib import Path

import pytest
from bodhiext.engine import DefaultSemanticEngine
from bodhilib import get_resource_queue, get_embedder, get_llm, get_splitter, get_vector_db


@pytest.fixture
def llm():
  return get_llm(service_name="openai_chat", model="gpt-3.5-turbo")


@pytest.fixture
def resource_queue():
  return get_resource_queue(service_name="in_memory")


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
def engine(llm, resource_queue, embedder, splitter, vector_db):
  engine = DefaultSemanticEngine(
    resource_queue=resource_queue,
    splitter=splitter,
    embedder=embedder,
    vector_db=vector_db,
    llm=llm,
    collection_name="test_collection",
  )
  engine.delete_collection()
  engine.create_collection()
  return engine


@pytest.fixture
def test_file():
  return str(Path(__file__).parent / "test_data" / "paul_graham_essay.txt")


@pytest.mark.live
def test_engine_rag(engine, test_file):
  engine.add_resource(file=str(test_file))
  engine.run_ingest()
  response = engine.rag("What are authors thought about painting?")
  print(response)
  assert "painting" in response.text

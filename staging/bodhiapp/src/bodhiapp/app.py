import asyncio
import logging
from contextlib import asynccontextmanager
from threading import Lock

from bodhiext.engine import DefaultSemanticEngine
from bodhilib import get_resource_queue, get_embedder, get_llm, get_splitter, get_vector_db
from dotenv import load_dotenv
from fastapi import Depends, FastAPI
from typing_extensions import Annotated

logging.basicConfig(level=logging.INFO)
load_dotenv(dotenv_path=".env.test")
service_lock = Lock()
search_engine = None


def get_search_engine() -> DefaultSemanticEngine:
  global search_engine
  with service_lock:
    if search_engine is None:
      llm = get_llm(service_name="openai_chat", model="gpt-3.5-turbo")
      resource_queue = get_resource_queue(service_name="in_memory")
      embedder = get_embedder(service_name="sentence_transformers")
      splitter = get_splitter(service_name="text_splitter", max_len=256, min_len=128, overlap=16)
      vector_db = get_vector_db(service_name="qdrant", host="localhost", port=6333)
      search_engine = DefaultSemanticEngine(
        resource_queue=resource_queue,
        splitter=splitter,
        embedder=embedder,
        vector_db=vector_db,
        llm=llm,
        collection_name="bodhiapp",
      )
  return search_engine


# @asynccontextmanager
# async def start_ingest(app: FastAPI):
#   search_engine = get_search_engine()
#   thread = threading.Thread(target=search_engine.ingest)
#   thread.daemon = True
#   thread.start()
#   yield


@asynccontextmanager
async def start_aingest(app: FastAPI):
  search_engine = get_search_engine()
  asyncio.create_task(search_engine.aingest())
  yield


# app = FastAPI(lifespan=start_ingest)
app = FastAPI(lifespan=start_aingest)


@app.post("/ingest_and_run")
async def ingest_and_run(path: str, service: Annotated[DefaultSemanticEngine, Depends(get_search_engine)]):
  service.add_resource(file=str(path))
  service.run_ingest()
  return {"message": "ingested"}


@app.post("/ingest")
async def ingest(path: str, service: Annotated[DefaultSemanticEngine, Depends(get_search_engine)]):
  service.add_resource(file=str(path))
  return {"message": "queued"}


@app.post("/aingest")
async def aingest(path: str, service: Annotated[DefaultSemanticEngine, Depends(get_search_engine)]):
  service.add_resource(file=str(path))
  return {"message": "aingested"}


@app.post("/rag")
async def rag(query: str, service: Annotated[DefaultSemanticEngine, Depends(get_search_engine)]):
  result = service.rag(query)
  return {"message": "rag", "result": result}


@app.post("/reset")
async def reset(service: Annotated[DefaultSemanticEngine, Depends(get_search_engine)]):
  service.delete_collection()
  service.create_collection()
  return {"message": "reset complete"}


@app.get("/ping")
async def ping():
  return {"message": "pong"}

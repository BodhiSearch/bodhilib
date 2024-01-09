from typing import AsyncIterator, Iterator, List, Literal, Optional, Union
import typing

from bodhilib import (
  DOCUMENT,
  LLM,
  AbstractResourceProcessor,
  Embedder,
  IsResource,
  Node,
  Splitter,
  VectorDB,
  to_document,
)
from bodhilib.logging import logger

from ..common._aiter import AsyncListIterator, abatch, batch


class DocumentVectorizer(AbstractResourceProcessor):
  def __init__(
    self,
    splitter: Splitter,
    embedder: Embedder,
    vector_db: VectorDB,
    llm: LLM,
    collection_name: str,
    distance: Optional[str] = "cosine",
  ) -> None:
    self.splitter = splitter
    self.embedder = embedder
    self.vector_db = vector_db
    self.llm = llm
    self.collection_name = collection_name
    self.distance = distance or "cosine"

  @typing.overload
  def process(self, resource: IsResource, stream: Optional[Literal[False]] = ...) -> List[IsResource]:
    ...

  @typing.overload
  def process(self, resource: IsResource, stream: Literal[True]) -> Iterator[IsResource]:
    ...

  def process(
    self, resource: IsResource, stream: Optional[bool] = False
  ) -> Union[List[IsResource], Iterator[IsResource]]:
    if resource.resource_type != DOCUMENT:
      raise ValueError(f"Expected resource type '{DOCUMENT}', got '{resource.resource_type}'")
    logger.info("[doc_vec] received resource")
    document = to_document(resource)
    nodes: List[Node] = self.splitter.split(document)
    batch_size = max(1, self.embedder.batch_size)
    for node_batch in batch(nodes, batch_size):
      embeddings: List[Node] = self.embedder.embed(node_batch)
      self.vector_db.upsert(self.collection_name, embeddings)
    logger.info("[process] process complete")
    if stream:
      return iter([])
    return []

  @typing.overload
  async def aprocess(self, resource: IsResource, astream: Optional[Literal[False]] = ...) -> List[IsResource]:
    ...

  @typing.overload
  async def aprocess(self, resource: IsResource, astream: Literal[True]) -> AsyncIterator[IsResource]:
    ...

  async def aprocess(
    self, resource: IsResource, astream: Optional[bool] = False
  ) -> Union[List[IsResource], AsyncIterator[IsResource]]:
    if resource.resource_type != DOCUMENT:
      raise ValueError(f"Expected resource type '{DOCUMENT}', got '{resource.resource_type}'")
    logger.info("[doc_vec] async received document")
    document = to_document(resource)
    nodes: AsyncIterator[Node] = self.splitter.split(document, astream=True)
    batch_size = max(1, self.embedder.batch_size)
    async for node_batch in abatch(nodes, batch_size):
      embeddings = self.embedder.embed(node_batch)
      self.vector_db.upsert(self.collection_name, embeddings)
    logger.info("[doc_vec] async process complete")
    if astream:
      return AsyncListIterator([])
    return []

  @property
  def supported_types(self) -> List[str]:
    return [DOCUMENT]

  @property
  def service_name(self) -> str:
    return "rag_resource_processor"

import logging
import textwrap
import typing
from typing import Any, AsyncIterator, Dict, List, Literal, Optional, Union

from bodhiext.common import abatch, batch
from bodhiext.prompt_template import StringPromptTemplate
from bodhilib import (
  LLM,
  DataLoader,
  Document,
  Embedder,
  Node,
  Prompt,
  PromptTemplate,
  SemanticSearchEngine,
  Splitter,
  TextLike,
  VectorDB,
  to_prompt,
)


class DefaultSemanticEngine(SemanticSearchEngine):
  def __init__(
    self,
    data_loader: DataLoader,
    splitter: Splitter,
    embedder: Embedder,
    vector_db: VectorDB,
    llm: LLM,
    collection_name: str,
    distance: Optional[str] = "cosine",
  ):
    self.data_loader = data_loader
    self.splitter = splitter
    self.embedder = embedder
    self.vector_db = vector_db
    self.llm = llm
    self.collection_name = collection_name
    self.distance = distance or "cosine"

  def add_resource(self, **kwargs: Dict[str, Any]) -> None:
    self.data_loader.push(**kwargs)

  def delete_collection(self) -> bool:
    return self.vector_db.delete_collection(self.collection_name)

  def create_collection(self) -> bool:
    return self.vector_db.create_collection(self.collection_name, self.embedder.dimension, self.distance)

  def run_ingest(self) -> None:
    docs = self.data_loader.load()
    for doc in docs:
      self._process_doc(doc)

  def ingest(self) -> None:
    while (doc := self.data_loader.pop()) is not None:
      logging.info("[ingest] received item")
      self._process_doc(doc)
      logging.info("[ingest] process complete")

  async def aingest(self) -> None:
    while (doc := await self.data_loader.apop()) is not None:
      logging.info("[aingest] received item")
      nodes: AsyncIterator[Node] = self.splitter.split(doc, astream=True)
      batch_size = max(1, self.embedder.batch_size)
      async for node_batch in abatch(nodes, batch_size):
        embeddings = self.embedder.embed(node_batch)
        self.vector_db.upsert(self.collection_name, embeddings)
      logging.info("[aingest] process complete")

  @typing.overload
  def ann(self, query: TextLike, *, n: Optional[int] = ...) -> List[Node]:
    ...

  @typing.overload
  def ann(self, query: TextLike, *, astream: Optional[Literal[False]], n: Optional[int] = ...) -> List[Node]:
    ...

  @typing.overload
  def ann(self, query: TextLike, *, astream: Literal[True], n: Optional[int] = ...) -> AsyncIterator[List[Node]]:
    ...

  def ann(
    self, query: TextLike, astream: Optional[bool] = None, n: Optional[int] = 5
  ) -> Union[List[Node], AsyncIterator[List[Node]]]:
    if astream:
      raise NotImplementedError("async ann is not implemented")
    prompt = to_prompt(query)
    embeddings = self.embedder.embed(prompt)
    result = self.vector_db.query(self.collection_name, embeddings[0])
    return result

  def rag(
    self,
    query: TextLike,
    prompt_template: Optional[PromptTemplate] = None,
    astream: Optional[bool] = False,
    n: Optional[int] = 5,
  ) -> Union[Prompt, AsyncIterator[Prompt]]:
    if astream:
      raise NotImplementedError("async answer is not implemented")
    contexts: List[Node] = self.ann(query, astream=astream, n=n)
    if prompt_template is None:
      text = """
        Below are snippets of document related to question at the end.
        Read and understand the context properly to answer the question.
        {% for context in contexts -%}
        {{ loop.index }}. {{context}}
        {% endfor %}
        Answer the question below based on the context provided above
        Question: {{query}}
      """
      text = textwrap.dedent(text).strip()
      prompt = Prompt(text=text)
      prompt_template = StringPromptTemplate(prompts=[prompt], metadata={"format": "jinja2"})
    prompts = prompt_template.to_prompts(contexts=contexts, query=query) # type: ignore
    response: Prompt = self.llm.generate(prompts, astream=astream) # type: ignore
    return response

  def _process_doc(self, doc: Document) -> None:
    nodes: List[Node] = self.splitter.split(doc)
    batch_size = max(1, self.embedder.batch_size)
    for node_batch in batch(nodes, batch_size):
      embeddings: List[Node] = self.embedder.embed(node_batch)
      self.vector_db.upsert(self.collection_name, embeddings)

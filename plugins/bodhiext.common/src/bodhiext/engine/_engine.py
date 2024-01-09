import textwrap
import typing
from typing import AsyncIterator, List, Literal, Optional, Union

from bodhiext.prompt_template import StringPromptTemplate
from bodhiext.resources import DefaultQueueProcessor
from bodhilib import (
  LLM,
  Embedder,
  IsResource,
  Node,
  Prompt,
  PromptTemplate,
  ResourceProcessorFactory,
  ResourceQueue,
  SemanticSearchEngine,
  Splitter,
  TextLike,
  VectorDB,
  to_prompt,
)

from ._doc_vec import DocumentVectorizer


class DefaultSemanticEngine(SemanticSearchEngine):
  def __init__(
    self,
    resource_queue: ResourceQueue,
    factory: ResourceProcessorFactory,
    splitter: Splitter,
    embedder: Embedder,
    vector_db: VectorDB,
    llm: LLM,
    collection_name: str,
    distance: Optional[str] = "cosine",
  ):
    self.resource_queue = resource_queue
    self.embedder = embedder
    self.vector_db = vector_db
    self.llm = llm
    self.collection_name = collection_name
    self.distance = distance or "cosine"
    document_vectorizer = DocumentVectorizer(splitter, embedder, vector_db, llm, collection_name, distance)
    self.queue_processor = DefaultQueueProcessor(resource_queue, factory)
    self.queue_processor.add_resource_processor(document_vectorizer)

  def add_resource(self, resource: IsResource) -> None:
    self.resource_queue.push(resource)

  def delete_collection(self) -> bool:
    return self.vector_db.delete_collection(self.collection_name)

  def create_collection(self) -> bool:
    return self.vector_db.create_collection(self.collection_name, self.embedder.dimension, self.distance)

  def run_ingest(self) -> None:
    self.queue_processor.process()

  def ingest(self) -> None:
    self.queue_processor.start()

  async def aingest(self) -> None:
    await self.queue_processor.astart()

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
    prompts = prompt_template.to_prompts(contexts=contexts, query=query)  # type: ignore
    response = self.llm.generate(prompts, astream=astream)
    return response

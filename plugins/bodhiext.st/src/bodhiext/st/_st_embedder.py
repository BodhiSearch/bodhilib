""":mod:`bodhiext.st` module defines classes and methods for embedder using sentence-transformer."""
from __future__ import annotations

import typing
from typing import Any, AsyncIterator, Dict, List, Literal, Optional, Union

import sentence_transformers as sentence_transformers
from bodhiext.common import AsyncListIterator
from bodhilib import Embedder, Embedding, Node, SerializedInput, Service, service_provider, to_node_list
from bodhilib.logging import logger

from ._version import __version__


class SentenceTransformerEmbedder(Embedder):
  """Embedder using sentence-transformer library."""

  def __init__(
    self,
    client: Optional[sentence_transformers.SentenceTransformer] = None,
    model: Optional[str] = None,
    **kwargs: Dict[str, Any],
  ) -> None:
    kwargs = {k: v for k, v in kwargs.items() if v is not None}
    self.kwargs = kwargs
    self.client: Optional[sentence_transformers.SentenceTransformer] = None
    if client:
      self.client = client
      return
    if model is None:
      logger.info("No model passed to SentenceTransformer. Using default model 'all-MiniLM-L6-v2'")
      self.model = "all-MiniLM-L6-v2"
    else:
      self.model = model

  @typing.overload
  def embed(self, inputs: SerializedInput) -> List[Node]:
    ...

  @typing.overload
  def embed(self, inputs: SerializedInput, astream: Optional[Literal[False]]) -> List[Node]:
    ...

  @typing.overload
  def embed(self, inputs: SerializedInput, astream: Literal[True]) -> AsyncIterator[Node]:
    ...

  def embed(self, inputs: SerializedInput, astream: Optional[bool] = None) -> Union[List[Node], AsyncIterator[Node]]:
    """Embeds the nodes using sentence-transformer.

    Args:
        nodes (List[:class:`~bodhilib.Node`]): list of nodes to embed
        astream (bool): whether to stream the embeddings (default: None)

    Returns:
        List[:class:`~bodhilib.Embedding`]: list of embeddings
    """
    nodes = to_node_list(inputs)
    if self.client is None:
      self.client = sentence_transformers.SentenceTransformer(self.model)
    embeddings: List[Embedding] = self.client.encode([node.text for node in nodes]).tolist()
    for node, embedding in zip(nodes, embeddings):
      node.embedding = embedding
    if astream is None or astream is False:
      return nodes
    return AsyncListIterator(nodes)

  @property
  def dimension(self) -> int:
    """Dimension of the embeddings.

    Returns:
        int: dimension of the embeddings
    """
    if self.client is None:
      self.client = sentence_transformers.SentenceTransformer(self.model)
    dimension = self.client.get_sentence_embedding_dimension()
    if dimension is None:
      raise ValueError("Dimension of the model is None.")
    if isinstance(dimension, int):
      return dimension
    raise ValueError(f"Unknown type for dimension, type={type(dimension)}")

  @property
  def batch_size(self) -> int:
    return 32


def sentence_transformer_builder(
  *,
  service_name: Optional[str] = None,
  service_type: Optional[str] = "embedder",
  client: Optional[sentence_transformers.SentenceTransformer] = None,
  model: Optional[str] = None,
  **kwargs: Dict[str, Any],
) -> SentenceTransformerEmbedder:
  """Returns an instance of sentence transformer builder.

  Args:
      service_name: service name to wrap, should be "sentence_transformers"
      service_type: service of the implementation, should be "embedder"
      client: the client to use for embedding, if not supplied, a new client is created
      model: the LLM model to use for embedding, if not supplied, a default is used
      **kwargs: pass through arguments for the embedder, e.g. dimension etc.
  """
  if service_name != "sentence_transformers":
    raise ValueError(f"Unknown service: {service_name=}")
  if service_type != "embedder":
    raise ValueError(f"Service type not supported: {service_type=}, supported service type: 'embedder'")
  return SentenceTransformerEmbedder(client=client, model=model, **kwargs)


@service_provider
def bodhilib_list_services() -> List[Service]:
  """Return a list of services supported by the plugin."""
  return [
    Service(
      service_name="sentence_transformers",
      service_type="embedder",
      publisher="bodhiext",
      service_builder=sentence_transformer_builder,
      version=__version__,
    )
  ]

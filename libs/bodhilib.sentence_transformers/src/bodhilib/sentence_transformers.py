""":mod:`bodhilib.sentence_transformers` module defines classes and methods for embedder using sentence-transformer."""
from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

from bodhilib.embedder import Embedder
from bodhilib.logging import logger
from bodhilib.plugin import Service, service_provider
from sentence_transformers import SentenceTransformer


class SentenceTransformerEmbedder(Embedder):
    """Embedder using sentence-transformer library."""

    def __init__(self, model: Optional[str] = None, **kwargs: Dict[str, Any]) -> None:
        if model is None:
            logger.info("No model passed to SentenceTransformer. Using default model 'all-MiniLM-L6-v2'")
            model = "all-MiniLM-L6-v2"
        self.model_name = model
        self.model: Optional[SentenceTransformer] = None

    def _embed(self, texts: Iterable[str]) -> Iterable[List[float]]:
        if self.model is None:
            self.model = SentenceTransformer(self.model_name)
        embeddings: List = self.model.encode(list(texts)).tolist()
        return iter(embeddings)

    @property
    def dimension(self) -> int:
        """Dimension of the embeddings."""
        if self.model is None:
            self.model = SentenceTransformer(self.model_name)
        dimension = self.model.get_sentence_embedding_dimension()
        if dimension is None:
            raise ValueError("Dimension of the model is None.")
        if isinstance(dimension, int):
            return dimension
        raise ValueError(f"Unknown type for dimension, type={type(dimension)}")


def sentence_transformer_builder(
    *,
    service_name: Optional[str] = None,
    service_type: Optional[str] = "embedder",
    model: Optional[str] = None,
    **kwargs: Dict[str, Any],
) -> SentenceTransformerEmbedder:
    """Returns an instance of sentence transformer builder.

    Args:
        service_name: service name to wrap, should be "sentence_transformers"
        service_type: service of the implementation, should be "embedder"
        model: the LLM model to use for embedding, if not supplied, a default is used
        **kwargs: pass through arguments for the embedder, e.g. dimension etc.
    """
    if service_name != "sentence_transformers":
        raise ValueError(f"Unknown service: {service_name=}")
    if service_type != "embedder":
        raise ValueError(f"Service type not supported: {service_type=}, supported service type: 'embedder'")
    return SentenceTransformerEmbedder(model=model, **kwargs)


@service_provider
def bodhilib_list_services() -> List[Service]:
    """Return a list of services supported by the plugin."""
    return [
        Service(
            service_name="sentence_transformers",
            service_type="embedder",
            publisher="bodhilib",
            service_builder=sentence_transformer_builder,
            version="0.1.0",
        )
    ]

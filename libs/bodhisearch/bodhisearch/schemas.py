from typing import Callable, NamedTuple


class Provider(NamedTuple):
    provider: str
    author: str
    type: str  # "llm", "vector_store", "embedder", "loader", "memory"
    func: Callable
    version: str = ""

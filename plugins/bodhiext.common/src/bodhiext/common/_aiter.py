from typing import AsyncIterator, Generic, List, TypeVar

T = TypeVar("T")


class AsyncListIterator(AsyncIterator[T], Generic[T]):
  def __init__(self, items: List[T]):
    self.items = items
    self.index = 0

  def __aiter__(self) -> AsyncIterator[T]:
    return self

  async def __anext__(self) -> T:
    if self.index < len(self.items):
      result = self.items[self.index]
      self.index += 1
      return result
    else:
      raise StopAsyncIteration

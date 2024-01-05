from typing import AsyncIterator, Generic, Iterator, List, TypeVar

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


def batch(iterable: List[T], batch_size: int) -> Iterator[List[T]]:
  list_size = len(iterable)
  for i in range(0, list_size, batch_size):
    yield iterable[i : i + batch_size]


async def abatch(iterator: AsyncIterator[T], batch_size: int) -> AsyncIterator[List[T]]:
  batch: List[T] = []
  async for item in iterator:
    batch.append(item)
    if len(batch) == batch_size:
      yield batch
      batch = []
  if len(batch) > 0:
    yield batch

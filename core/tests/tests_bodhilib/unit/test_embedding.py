import pytest
from bodhilib import Node, to_embedding


class _TestEmbedding:
  @property
  def embedding(self):
    return [1.0, 2.0, 3.0]


@pytest.mark.parametrize(
  "valid_arg",
  [
    (Node(text="hello", embedding=[1.0, 2.0, 3.0])),
    (_TestEmbedding()),
    ([1.0, 2.0, 3.0]),
  ],
)
def test_embedding_to_embedding(valid_arg):
  embeddings = to_embedding(valid_arg)
  assert embeddings == [1.0, 2.0, 3.0]


def test_embedding_raises_exception_for_invalid_arg():
  with pytest.raises(ValueError) as e:
    _ = to_embedding(object())
  assert str(e.value) == "Cannot convert type <class 'object'> to embedding."

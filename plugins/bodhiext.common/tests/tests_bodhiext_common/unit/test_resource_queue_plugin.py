import pytest
from bodhiext.resources import InMemoryResourceQueue
from bodhilib import get_resource_queue


class _TestQueue:
  ...


def test_resource_queue_raises_type_error_if_not_of_given_type():
  with pytest.raises(TypeError) as e:
    _ = get_resource_queue("in_memory", oftype=_TestQueue)
  expected = (
    "Expecting resource_queue of type \"<class 'tests_bodhiext_common.unit.test_resource_queue_plugin._TestQueue'>\", "
    "but got \"<class 'bodhiext.resources._queue.InMemoryResourceQueue'>\""
  )
  assert str(e.value) == expected


def test_resource_queue_package_plugins():
  queue = get_resource_queue("in_memory", publisher="bodhiext", oftype=InMemoryResourceQueue)
  assert isinstance(queue, InMemoryResourceQueue)

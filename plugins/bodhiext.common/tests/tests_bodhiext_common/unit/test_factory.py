import pytest
from bodhiext.resources import DefaultFactory, GlobProcessor, LocalDirProcessor, LocalFileProcessor, TextPlainProcessor


@pytest.fixture
def factory():
  return DefaultFactory()


@pytest.mark.parametrize(
  ["supported_type", "service_name", "service_class"],
  [
    ("local_file", "local_file", LocalFileProcessor),
    ("local_dir", "local_dir", LocalDirProcessor),
    ("glob", "glob", GlobProcessor),
    ("text/plain", "text_plain", TextPlainProcessor),
  ],
)
def test_factory_find(factory, supported_type, service_name, service_class):
  processor_service = factory.find(supported_type)
  assert len(processor_service) == 1
  assert processor_service[0].service_name == service_name
  assert isinstance(processor_service[0], service_class)

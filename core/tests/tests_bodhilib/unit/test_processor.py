from typing import List

from bodhilib import AbstractResourceProcessor, IsResource, ResourceProcessor


class _TestProcessor(AbstractResourceProcessor):
  def process(self, resource: IsResource) -> List[IsResource]:
    return []

  async def aprocess(self, resource: IsResource) -> List[IsResource]:
    return []

  @property
  def supported_types(self) -> List[str]:
    return ["test"]

  @property
  def service_name(self) -> str:
    return "test_processor"


def test_processor_abstract_conforms_resource_processor_protocol():
  processor = _TestProcessor()
  assert isinstance(processor, ResourceProcessor)

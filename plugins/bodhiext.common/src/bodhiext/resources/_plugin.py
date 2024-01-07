from typing import List

from bodhiext.common._version import __version__
from bodhilib import RESOURCE_QUEUE, Service, service_provider

from ..common._constants import IN_MEMORY_SERVICE
from ._queue import resource_queue_service_builder as resource_queue_service_builder


@service_provider
def bodhilib_list_services() -> List[Service]:
  """Return a list of services supported by the bodhiext resource_queues package."""
  return [
    Service(
      service_name=IN_MEMORY_SERVICE,
      service_type=RESOURCE_QUEUE,
      publisher="bodhiext",
      service_builder=resource_queue_service_builder,
      version=__version__,
    )
  ]

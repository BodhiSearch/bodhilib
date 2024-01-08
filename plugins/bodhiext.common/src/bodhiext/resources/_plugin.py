from typing import List

from bodhiext.common._version import __version__
from bodhilib import RESOURCE_FACTORY, RESOURCE_PROCESSOR, RESOURCE_QUEUE, Service, service_provider

from ..common._constants import DEFAULT_RESOURCE_FACTORY, IN_MEMORY_SERVICE
from ._processor import SUPPORTED_PROCESSORS, resource_factory_service_builder, resource_processor_service_builder
from ._queue import resource_queue_service_builder


@service_provider
def bodhilib_list_services() -> List[Service]:
  """Return a list of services supported by the bodhiext resource_queues package."""
  services = []
  for name, supported_types in SUPPORTED_PROCESSORS.items():
    services.append(
      Service(
        service_name=name,
        service_type=RESOURCE_PROCESSOR,
        publisher="bodhiext",
        service_builder=resource_processor_service_builder,
        version=__version__,
        metadata={"supported_types": supported_types},
      )
    )
  return [
    Service(
      service_name=IN_MEMORY_SERVICE,
      service_type=RESOURCE_QUEUE,
      publisher="bodhiext",
      service_builder=resource_queue_service_builder,
      version=__version__,
    ),
    Service(
      service_name=RESOURCE_FACTORY,
      service_type=DEFAULT_RESOURCE_FACTORY,
      publisher="bodhiext",
      service_builder=resource_factory_service_builder,
      version=__version__,
    ),
  ] + services

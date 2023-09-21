from typing import List

from bodhilib.plugin import Service, service_provider

from ._file import file_loader_service_builder as file_loader_service_builder


@service_provider
def bodhilib_list_services() -> List[Service]:
    """Return a list of services supported by the bodhiext data_loaders package."""
    return [
        Service(
            service_name="file",
            service_type="data_loader",
            publisher="bodhiext",
            service_builder=file_loader_service_builder,
            version="0.1.0",
        )
    ]
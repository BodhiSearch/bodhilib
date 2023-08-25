"""Plugin related code for bodhilib."""
import itertools
import sys
from typing import Any, Callable, Dict, List, NamedTuple, Optional

import pluggy
from bodhilib.common import package_name
from bodhilib.logging import logger

hookspec = pluggy.HookspecMarker(package_name)
service_provider = pluggy.HookimplMarker(package_name)
current_module = sys.modules[__name__]


class Service(NamedTuple):
    """Encapsulates basic info of service provided by the plugin."""

    service_name: str
    service_type: str
    publisher: str
    service_builder: Callable  # signature(**kwargs: Dict[str, Any])
    version: str = ""


@hookspec
def bodhilib_list_services() -> List[Service]:
    """Return a list of services supported by plugin.

    When user request for service using service_name and service_type, this information is matched,
    and the service_builder method of the plugin is called with all info.

    Returns:
        List[Service]: list of services supported by plugin
    """
    return []


class PluginManager:
    """Searches for and loads bodhilib plugins."""

    _instance = None

    def __new__(cls) -> "PluginManager":
        """Override `__new__` incase constructor is directly called."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def instance(cls) -> "PluginManager":
        """Singleton method to return instance of PluginManager."""
        # extracting in variable because of mypy warning
        instance = cls._instance
        if instance is None:
            return cls()
        return instance

    def __init__(self) -> None:
        """Initialize plugin manager and load the bodhilib plugins."""
        pm = pluggy.PluginManager(package_name)
        pm.add_hookspecs(current_module)
        pm.load_setuptools_entrypoints(package_name)
        # TODO remove after moving openai plugin to separate repo
        import bodhilib.openai as bodhilib_openai

        pm.register(bodhilib_openai)
        self.pm = pm
        self.services: Optional[List[Service]] = None

    def get(self, service_name: str, service_type: str, **kwargs: Dict[str, Any]) -> Any:
        """Get an instance of service for the given service and type."""
        self.services = self.services or self._fetch_services()
        for service in self.services:
            if service.service_name == service_name and service.service_type == service_type:
                all_args = {**{"service_name": service_name, "service_type": service_type}, **kwargs}
                component = service.service_builder(**all_args)
                return component
        raise ValueError(f"Unknown service: {service_name}, available services: {self.services}")

    def _fetch_services(self) -> List[Service]:
        logger.debug({"msg": "fetching services"})
        services = list(itertools.chain(*self.pm.hook.bodhilib_list_services()))
        logger.debug({"msg": "fetched services", "services": services})
        # get list of services which are not instance of Service and log with warning
        invalid_services = [p for p in services if not isinstance(p, Service)]
        if invalid_services:
            logger.warning({"msg": "invalid services, ignoring", "services": invalid_services})
        # get list of valid services and log with debug
        valid_services = [p for p in services if isinstance(p, Service)]
        logger.debug({"msg": "valid services", "services": valid_services})
        return valid_services

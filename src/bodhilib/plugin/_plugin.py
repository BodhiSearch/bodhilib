from __future__ import annotations

import itertools
import sys
from typing import Any, Callable, List, NamedTuple, Optional, Type, TypeVar, cast

import pluggy
from bodhilib.core import package_name
from bodhilib.logging import logger

hookspec = pluggy.HookspecMarker(package_name)
service_provider = pluggy.HookimplMarker(package_name)
current_module = sys.modules[__name__]


class Service(NamedTuple):
    """Encapsulates basic info of service provided by the plugin."""

    service_name: str
    """Name of the service provided by the plugin. E.g. openai, cohere, anthropic, etc."""
    service_type: str
    """Type of service provided by the plugin. E.g. llm, embed etc."""
    publisher: str
    """Publisher identifier of the plugin. E.g. bodhilib, openai, <github-user> etc."""
    service_builder: Callable  # signature(**kwargs: Dict[str, Any])
    """Callable which returns an instance of service.

    Callable takes in `**kwargs: Dict[str, Any]` and returns an instance of service.
    """
    version: str = ""
    """Version of the plugin"""


@hookspec
def bodhilib_list_services() -> List[Service]:
    """Return a list of services supported by plugin.

    When user request for service using service_name and service_type, this information is matched,
    and the service_builder method of the plugin is called with all info.

    Returns:
        List[Service]: list of services supported by plugin
    """
    return []


class LLMModel(NamedTuple):
    """Encapsulates the models provided by the service."""

    service_name: str
    """Name of the service identifier. E.g. openai, cohere, anthropic, etc."""

    model_name: str
    """Name of the LLM model provided by the service."""

    publisher: str
    """Publisher identifier of the plugin. E.g. bodhilib, openai, <github-user> etc."""


@hookspec
def bodhilib_list_llm_models() -> List[LLMModel]:
    """Return a list of LLM models supported by plugin.

    Returns:
        List[LLMModel]: list of LLM models supported by plugin
    """
    return []


T = TypeVar("T")
"""TypeVar for Component (one of sub-class of :class:`~bodhilib.llm.LLM`, :class:`~bodhilib.embedder.Embedder`,
:class:`~bodhilib.data_loader.DataLoader`).
Used for type hinting in :meth:`~bodhilib.plugin.PluginManager.get` method."""


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
        self.pm = pm
        self.services: Optional[List[Service]] = None

    def get(
        self,
        service_name: str,
        service_type: str,
        *,
        oftype: Optional[Type[T]] = None,
        publisher: Optional[str] = None,
        version: Optional[str] = None,
        **kwargs: Any,
    ) -> T:
        """Get an instance of service for the given service and type.

        Args:
            service_name (str): name of the service, e.g. "openai", "cohere", "anthropic"
            service_type (str): type of the service, e.g. "llm", "embedder", "data_loader"
            oftype (Optional[Type[T]]): if the type of service is known, pass the type in argument `oftype`,
                the service is cast to `oftype` and returned for better IDE support.
            publisher (Optional[str]): publisher or developer of the service plugin, e.g. "bodhilib","<github-username>"
            version (Optional[str]): version of the service
            **kwargs (Dict[str, Any]): pass through arguments for the service, e.g. "temperature", "max_tokens", etc.

        Returns:
            T (:data:`~bodhilib.plugin._plugin.T` | :class:`~Any`):
                an instance of service of type `oftype`, if oftype is passed, else of type :class:`~typing.Any`

        Raises:
            TypeError: if the type of service is not oftype
        """
        if oftype is None:
            return_type: Type[Any] = type(Any)
        else:
            return_type = oftype
        if self.services is None:
            self.services = self._fetch_services()
        all_args = {
            "service_name": service_name,
            "service_type": service_type,
            "publisher": publisher,
            "version": version,
            **kwargs,
        }
        for service in self.services:
            if service.service_name == service_name and service.service_type == service_type:
                component = service.service_builder(**all_args)
                if not isinstance(component, return_type):
                    raise TypeError(f"Expected {type(component)} to be {oftype=}")
                return cast(T, component)
        raise ValueError(f"Unknown service: {service_name}, available services: {self.services}")

    def list_services(self, service_type: str) -> List[Service]:
        """List all services of type service_type installed and available."""
        if self.services is None:
            self.services = self._fetch_services()
        return [s for s in self.services if s.service_type == service_type]

    def list_llm_models(self) -> List[LLMModel]:
        """List all LLM models installed and available."""
        logger.debug({"msg": "fetching plugins implementing list_llm_models"})
        llm_models = list(itertools.chain(*self.pm.hook.bodhilib_list_llm_models()))
        # filter out invalid LLM models
        llm_models = [p for p in llm_models if isinstance(p, LLMModel)]
        return llm_models

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

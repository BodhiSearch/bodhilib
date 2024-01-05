from typing import Any, Callable, List, NamedTuple, Optional, Type, TypeVar

from _typeshed import Incomplete
from bodhilib.common import package_name as package_name
from bodhilib.logging import logger as logger

hookspec: Incomplete
service_provider: Incomplete
current_module: Incomplete

class Service(NamedTuple):
  service_name: str
  service_type: str
  publisher: str
  service_builder: Callable
  version: str = ...

def bodhilib_list_services() -> List[Service]: ...

C = TypeVar("C")

class PluginManager:
  def __new__(cls) -> PluginManager: ...
  @classmethod
  def instance(cls) -> PluginManager: ...
  pm: Incomplete
  services: Incomplete
  def __init__(self) -> None: ...
  def get(
    self,
    service_name: str,
    service_type: str,
    *,
    oftype: Optional[Type[C]] = None,
    publisher: Optional[str] = None,
    version: Optional[str] = None,
    **kwargs: Any,
  ) -> C: ...
  def list_services(self, service_type: str) -> List[Service]: ...

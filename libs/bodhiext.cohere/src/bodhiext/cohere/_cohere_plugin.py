"""LLM implementation for Cohere."""
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from bodhilib import LLM, Service, service_provider

import cohere

from ._cohere_llm import Cohere
from ._version import __version__


@service_provider
def bodhilib_list_services() -> List[Service]:
    """This function is used by bodhilib to find all services in this module."""
    return [
        Service(
            service_name="cohere",
            service_type="llm",
            publisher="bodhiext",
            service_builder=cohere_llm_service_builder,
            version=__version__,
        )
    ]


def cohere_llm_service_builder(
    *,
    service_name: Optional[str] = None,
    service_type: Optional[str] = "llm",
    client: Optional[cohere.Client] = None,
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    **kwargs: Dict[str, Any],
) -> LLM:
    """Returns an instance of Cohere LLM service implementing :class:`bodhilib.LLM`.

    Args:
        service_name: service name to wrap, should be "cohere"
        service_type: service type of the implementation, should be "llm"
        client: Cohere client instance, if not set, it will be created using other parameters
        model: Cohere model identifier
        api_key: api key for Cohere service, if not set, it will be read from environment variable COHERE_API_KEY
    Returns:
        LLM: a service instance implementing :class:`bodhilib.LLM` for the given service and model
    Raises:
        ValueError: if service_name is not "cohere"
        ValueError: if service_type is not "llm"
        ValueError: if model is not set
        ValueError: if api_key is not set, and environment variable COHERE_API_KEY is not set
    """
    # TODO use pydantic for parameter validation
    if service_name != "cohere" or service_type != "llm":
        raise ValueError(
            f"Unknown params: {service_name=}, {service_type=}, supported params: service_name='cohere',"
            " service_type='llm'"
        )
    if api_key is None:
        if os.environ.get("COHERE_API_KEY") is None:
            raise ValueError("environment variable COHERE_API_KEY is not set")
        else:
            api_key = os.environ["COHERE_API_KEY"]
    return Cohere(client=client, model=model, api_key=api_key, **kwargs)

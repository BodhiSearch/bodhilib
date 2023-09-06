"""Plugin code for OpenAI services."""
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional, Union

from bodhilib.plugin import LLMModel, Service, service_provider

import openai

from ._openai_llm import OpenAIChat, OpenAIText


@service_provider
def bodhilib_list_services() -> List[Service]:
    """Return a list of services supported by the plugin."""
    return [
        Service(
            service_name="openai",
            service_type="llm",
            publisher="bodhilib",
            service_builder=openai_llm_service_builder,
            version="0.1.0",
        )
    ]


def openai_llm_service_builder(
    *,
    service_name: Optional[str] = None,
    service_type: Optional[str] = "llm",
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    **kwargs: Dict[str, Any],
) -> Union[OpenAIChat, OpenAIText]:
    """Returns an instance of LLM for the given arguments.

    Args:
        service_name: service name to wrap, should be "openai"
        service_type: service of the implementation, should be "llm"
        model: OpenAI model identifier
        api_key: OpenAI api key, if not set, it will be read from environment variable OPENAI_API_KEY
        **kwargs: additional arguments passed to the OpenAI API client
    Returns:
        LLM: an instance of LLM for the given service, and model
    Raises:
        ValueError: if service_name is not "openai"
        ValueError: if service_type is not "llm"
        ValueError: if model is not set
        ValueError: if api_key is not set and environment variable OPENAI_API_KEY is not set
    """
    # TODO replace with pydantic validations
    if service_name != "openai":
        raise ValueError(f"Unknown service: {service_name=}")
    if service_type != "llm":
        raise ValueError(f"Service type not supported: {service_type=}, supported service types: llm")
    if model is None:
        raise ValueError("model is not set")
    if api_key is None:
        if os.environ.get("OPENAI_API_KEY") is None:
            raise ValueError("environment variable OPENAI_API_KEY is not set")
        else:
            openai.api_key = os.environ["OPENAI_API_KEY"]
    else:
        openai.api_key = api_key
    params: Dict[str, Any] = {**{"api_key": api_key}, **kwargs}
    if model.startswith("gpt"):
        return OpenAIChat(model, **params)
    else:
        return OpenAIText(model, **params)


# TODO: cache the response
@service_provider
def bodhilib_list_llm_models() -> List[LLMModel]:
    """Plugin function to list all LLM models available by this service."""
    models = openai.Model.list()
    llm_models = [LLMModel("openai", m["id"], "bodhilib") for m in models.data]
    return llm_models

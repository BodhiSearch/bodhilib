"""Plugin code for OpenAI services."""
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from bodhilib import Service, service_provider

import openai

from ._openai_llm import OpenAIChat, OpenAIText
from ._version import __version__


@service_provider
def bodhilib_list_services() -> List[Service]:
    """Return a list of services supported by the plugin."""
    return [
        Service(
            service_name="openai_chat",
            service_type="llm",
            publisher="bodhiext",
            service_builder=openai_chat_service_builder,
            version=__version__,
        ),
        Service(
            service_name="openai_text",
            service_type="llm",
            publisher="bodhiext",
            service_builder=openai_text_service_builder,
            version=__version__,
        ),
    ]


def openai_text_service_builder(
    *,
    service_name: Optional[str] = None,
    service_type: Optional[str] = "llm",
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    **kwargs: Dict[str, Any],
) -> OpenAIText:
    """Returns an instance of OpenAIText LLM for the given arguments.

    Args:
        service_name (Optional[str]): service name to wrap, should be "openai_text"
        service_type (Optional[str]): service of the implementation, should be "llm"
        model (Optional[str]): OpenAI model identifier, e.g. text-ada-002
        api_key (Optional[str]): OpenAI api key, if not set, it will be read from environment variable OPENAI_API_KEY
        **kwargs: additional pass through arguments for OpenAI API client

    Returns:
        OpenAIText: an instance of OpenAIText implementing :class:`bodhilib.LLM`

    Raises:
        ValueError: if service_name is not "openai_text" or service_type is not "llm"
        ValueError: if api_key is not set and environment variable OPENAI_API_KEY is not set
    """
    if service_name != "openai_text" or service_type != "llm":
        raise ValueError(
            f"Unknown params: {service_name=}, {service_type=}, supported params: service_name='openai_text',"
            " service_type='llm'"
        )
    _set_openai_api_key(api_key)
    all_args: Dict[str, Any] = {"model": model, "api_key": api_key, **kwargs}
    all_args = {k: v for k, v in all_args.items() if v is not None}
    return OpenAIText(**all_args)


def openai_chat_service_builder(
    *,
    service_name: Optional[str] = None,
    service_type: Optional[str] = "llm",
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    **kwargs: Dict[str, Any],
) -> OpenAIChat:
    """Returns an instance of OpenAIChat LLM for the given arguments.

    Args:
        service_name: service name to wrap, should be "openai_chat"
        service_type: service type of the component, should be "llm"
        model: OpenAI chat model identifier, e.g. gpt-3.5-turbo
        api_key: OpenAI api key, if not set, it will be read from environment variable OPENAI_API_KEY
        **kwargs: additional arguments passed to the OpenAI API client

    Returns:
        OpenAIChat: an instance of OpenAIChat implementing :class:`bodhilib.LLM`

    Raises:
        ValueError: if service_name is not "openai" or service_type is not "llm"
        ValueError: if api_key is not set and environment variable OPENAI_API_KEY is not set
    """
    if service_name != "openai_chat" or service_type != "llm":
        raise ValueError(
            f"Unknown params: {service_name=}, {service_type=}, supported params: service_name='openai_chat',"
            " service_type='llm'"
        )
    _set_openai_api_key(api_key)
    all_args: Dict[str, Any] = {"model": model, "api_key": api_key, **kwargs}
    all_args = {k: v for k, v in all_args.items() if v is not None}
    return OpenAIChat(**all_args)


def _set_openai_api_key(api_key: Optional[str]) -> None:
    if api_key is None:
        if os.environ.get("OPENAI_API_KEY") is None:
            raise ValueError("environment variable OPENAI_API_KEY is not set")
        else:
            openai.api_key = os.environ["OPENAI_API_KEY"]
    else:
        openai.api_key = api_key

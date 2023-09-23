from typing import Any, Dict, List, Optional

from bodhilib import Service, service_provider

from ._text_splitter import TextSplitter
from ._version import __version__


def text_splitter_service_builder(
    *,
    service_name: Optional[str] = "text_splitter",
    service_type: Optional[str] = "splitter",
    publisher: Optional[str] = "bodhiext",
    version: Optional[str] = None,
    max_len: Optional[int] = None,
    min_len: Optional[int] = None,
    overlap: Optional[int] = None,
    eos_patterns: Optional[List[str]] = None,
    eow_patterns: Optional[List[str]] = None,
    **kwargs: Dict[str, Any],
) -> TextSplitter:
    """Service builder for text splitter."""
    if service_name != "text_splitter" or service_type != "splitter" or publisher != "bodhiext":
        raise ValueError(
            f"Unknown service: {service_name=}, {service_type=}, {publisher=}, "
            "supported service: service_name='text_splitter', service_type='splitter', publisher='bodhiext'"
        )
    all_args = {
        "max_len": max_len,
        "min_len": min_len,
        "overlap": overlap,
        "eos_patterns": eos_patterns,
        "eow_patterns": eow_patterns,
        **kwargs,
    }
    all_args = {k: v for k, v in all_args.items() if v is not None}
    # TODO: Add validation for all_args, extra args fails the constructor
    return TextSplitter(**all_args)  # type: ignore


@service_provider
def bodhilib_list_services() -> List[Service]:
    """Return a list of services supported by the bodhiext data_loaders package."""
    return [
        Service(
            service_name="text_splitter",
            service_type="splitter",
            publisher="bodhiext",
            service_builder=text_splitter_service_builder,
            version=__version__,
        )
    ]

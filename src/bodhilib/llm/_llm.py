from __future__ import annotations

import abc
import itertools
from typing import Any, Dict, Iterator, List, Optional, Union, cast, no_type_check

from bodhilib.models import Prompt
from bodhilib.plugin import PluginManager
from typing_extensions import TypeAlias

PromptInput: TypeAlias = Union[str, List[str], Prompt, List[Prompt], Dict[str, Any], List[Dict[str, Any]]]
"""Documentation for typealias should be direcly edited in the rst file."""


def parse_prompts(input: PromptInput) -> List[Prompt]:
    """Parses from the PromptInput to List[Prompt].

    Args:
        input (:data:`PromptInput`): input to parse from
    """
    if isinstance(input, str):
        return [Prompt(input)]
    if isinstance(input, Prompt):
        return [input]
    if isinstance(input, dict):
        return [Prompt(**input)]
    if isinstance(input, list):
        result = [parse_prompts(p) for p in input]
        return list(itertools.chain(*result))
    raise TypeError(f"Unknown prompt type: {type(input)}")


class LLM(abc.ABC):
    """Abstract Base Class LLM defines the common interface implemented by all LLM implementations."""

    def generate(
        self,
        prompts: PromptInput,
        *,
        stream: Optional[bool] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        n: Optional[int] = None,
        stop: Optional[List[str]] = None,
        max_tokens: Optional[int] = None,
        presence_penalty: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        user: Optional[str] = None,
        **kwargs: Dict[str, Any],
    ) -> Union[Prompt, Iterator[Prompt]]:
        """Base class :func:`~bodhilib.llm.LLM.generate` method interface common to all LLM service implementation.

        Takes in :data:`PromptInput`, a flexible input supporting from plain string, :class:`~bodhilib.models.Prompt`
        object, to dict representation of Prompt. Returns the response from LLM service as
        :class:`~bodhilib.models.Prompt` object with `source="output"`.

        Args:
            prompts (:data:`PromptInput`): input to the LLM service
            stream (bool): whether to stream the response from the LLM service
            temperature (Optional[float]): temperature or randomness of the generation
            top_p (Optional[float]): token consideration probability top_p for the generation
            top_k (Optional[int]): token consideration number top_k for the generation
            n (Optional[int]): number of responses to generate
            stop (Optional[List[str]]): list of stop tokens to stop the generation
            max_tokens (Optional[int]): maximum number of tokens to generate
            presence_penalty (Optional[float]): presence penalty for the generation, between -2 and 2
            frequency_penalty (Optional[float]): frequency penalty for the generation, between -2 and 2
            user (Optional[str]): user making the request, for monitoring purpose
            kwargs (Dict[str, Any]): pass through arguments for the LLM service

        Returns:
            :class:`~bodhilib.models.Prompt`: a Prompt object, if stream is False
            Iterator[:class:`~bodhilib.models.Prompt`]: an iterator of Prompt objects, if stream is True
        """
        prompts = parse_prompts(prompts)
        all_args = {
            "stream": stream,
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "n": n,
            "stop": stop,
            "max_tokens": max_tokens,
            "presence_penalty": presence_penalty,
            "frequency_penalty": frequency_penalty,
            "user": user,
            **kwargs,
        }
        return self._generate(prompts, **all_args)  # type: ignore

    @no_type_check
    @abc.abstractmethod
    def _generate(
        self,
        prompts: List[Prompt],
        *,
        stream: Optional[bool] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        n: Optional[int] = None,
        stop: Optional[List[str]] = None,
        max_tokens: Optional[int] = None,
        presence_penalty: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        user: Optional[str] = None,
        **kwargs: Dict[str, Any],
    ) -> Union[Prompt, Iterator[Prompt]]:
        """Generate text using LLM service with the given prompt list.

        This method should be implemented by the LLM service plugin.
        The PromptInput received in :func:`~bodhilib.llm.LLM.generate` is parsed into a list of
        :class:`~bodhilib.models.Prompt` and passed to this method.

        Args:
            prompts (List[:class:`~bodhilib.models.Prompt`]): list of prompts as input to the LLM service
            stream (bool): whether to stream the response from the LLM service
            temperature (Optional[float]): temperature or randomness of the generation
            top_p (Optional[float]): token consideration probability top_p for the generation
            top_k (Optional[int]): token consideration number top_k for the generation
            n (Optional[int]): number of responses to generate
            stop (Optional[List[str]]): list of stop tokens to stop the generation
            max_tokens (Optional[int]): maximum number of tokens to generate
            presence_penalty (Optional[float]): presence penalty for the generation, between -2 and 2
            frequency_penalty (Optional[float]): frequency penalty for the generation, between -2 and 2
            user (Optional[str]): user making the request, for monitoring purpose
            kwargs (Dict[str, Any]): pass through arguments for the LLM service

        Returns:
            :class:`~bodhilib.models.Prompt`: response as a Prompt object, if stream is False
            Iterator[:class:`~bodhilib.models.Prompt`]: an iterator of Prompt objects, if stream is True
        """
        ...


def get_llm(
    service_name: str,
    model: str,
    api_key: Optional[str] = None,
    *,
    publisher: Optional[str] = None,
    version: Optional[str] = None,
    **kwargs: Dict[str, Any],
) -> LLM:
    """Get an instance of LLM for the given service name and model.

    Args:
        service_name (str): name of the service, e.g. "openai", "cohere", "anthropic"
        model (str): name of the model, e.g. "chat-gpt-3.5", "command", "claude-2"
        api_key (Optional[str]): API key for the service, if the api_key is not provided,
            it will be looked in the environment variables
        publisher (Optional[str]): publisher or developer of the service plugin, e.g. "bodhilib", "<github-username>"
        version (Optional[str]): version of the service
        **kwargs (Dict[str, Any]): pass through arguments for the LLM service, e.g. "temperature", "max_tokens", etc.

    Returns:
        LLM: instance of LLM
    """
    manager = PluginManager.instance()
    llm = manager.get(
        service_name=service_name,
        service_type="llm",
        model=model,
        api_key=api_key,
        publisher=publisher,
        version=version,
        **kwargs,
    )
    return cast(LLM, llm)

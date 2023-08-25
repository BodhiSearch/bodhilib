"""bodhilib :class:`bodhilib.llm.LLM` implementation for OpenAI API."""
import os
from typing import Any, Dict, Iterable, List, NoReturn, Optional, Union

from bodhilib.llm import LLM
from bodhilib.plugin import Provider, provider
from bodhilib.prompt import Prompt, PromptInput, parse_prompts

import openai


@provider
def bodhilib_get_providers() -> List[Provider]:
    """Return a list of provider classes to be registered with the provider."""
    return [Provider("openai", "bodhilib", "llm", get_llm, "0.1.0")]


class OpenAIChat(LLM):
    """OpenAI Chat API implementation for :class:`bodhilib.llm.LLM`."""

    def __init__(self, model: str, **kwargs: Dict[str, Any]) -> None:
        self.model = model
        self.kwargs = kwargs

    def generate(self, prompts: PromptInput, **kwargs: Dict[str, Any]) -> Prompt:
        parsed_prompts = parse_prompts(prompts)
        # list of parameters accepted by .create functions
        # ref: https://platform.openai.com/docs/api-reference/chat-completions/create
        # model:str, []messages[role['system', 'user', 'assistant', 'function'], content:str?,
        #       name:str?(required for function call),
        #       function_call[name:str, arguments:str]],
        # functions, function_call, temperature, top_p, n, stream, stop, max_tokens, presence_penalty,
        # frequency_penalty, logit_bias, user
        # Returns:
        # id: str, object: str, created: int, model: str,[]choices:[index:str,
        #       message: [role, content, function_call: obj], finish_reason: str],
        #       usage: [prompt_tokens: int, completion_tokens: int, total_tokens: int],
        varags = {**self.kwargs, **kwargs}
        varags = {k: v for k, v in varags.items() if v is not None}
        completion = openai.ChatCompletion.create(
            model=self.model, messages=self._to_messages(parsed_prompts), **varags
        )
        response = completion.choices[0].message["content"]
        return Prompt(response, role="ai", source="output")

    def _to_messages(self, prompts: List[Prompt]) -> List[Dict[str, str]]:
        return [{"role": p.role, "content": p.text} for p in prompts]

    def __call__(self, *args: Iterable[Any], **kwargs: Dict[str, Any]) -> NoReturn:
        raise TypeError(f"'{type(self).__name__}' object is not callable, did you mean to call 'generate'?")


class OpenAIClassic(LLM):
    """OpenAI Classic API implementation for :class:`bodhilib.llm.LLM`."""

    def __init__(self, model: str, **kwargs: Dict[str, Any]) -> None:
        self.model = model
        self.kwargs = kwargs

    def generate(self, prompts: PromptInput, **kwargs: Any) -> Prompt:
        parsed_prompts = parse_prompts(prompts)
        prompt = self._to_prompt(parsed_prompts)
        result = openai.Completion.create(model=self.model, prompt=prompt, **kwargs)
        response = result.choices[0]["text"]
        return Prompt(response, role="ai", source="output")

    def _to_prompt(self, prompts: List[Prompt]) -> str:
        return "\n".join([p.text for p in prompts])

    def __call__(self, *args: Iterable[Any], **kwargs: Dict[str, Any]) -> NoReturn:
        raise TypeError(f"'{type(self).__name__}' object is not callable, did you mean to call 'generate'?")


def get_llm(
    provider: str, model: str, api_key: Optional[str] = None, **kwargs: Dict[str, Any]
) -> Union[OpenAIChat, OpenAIClassic]:
    """Returns an instance of LLM for the given provider.

    Args:
        provider (str): provider name
        model (str): model name
        api_key (str): api key
        kwargs (Dict[str, Any]): additional arguments
    Returns:
        LLM: an instance of LLM for the given provider
    Raises:
        ValueError: if provider is not "openai"
        ValueError: if api_key is not set
    """
    if provider != "openai":
        raise ValueError(f"Unknown provider: {provider}")
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
        return OpenAIClassic(model, **params)

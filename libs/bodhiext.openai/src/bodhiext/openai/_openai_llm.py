"""OpenAI LLM module."""
from __future__ import annotations

from typing import Any, Dict, Iterable, List, NoReturn, Optional, Union

from bodhilib import LLM, Prompt, PromptStream, Role, SerializedInput, prompt_output, to_prompt_list

import openai
from openai.openai_response import OpenAIResponse


class OpenAIChat(LLM):
    """OpenAI Chat API implementation for :class:`bodhilib.LLM`."""

    def __init__(self, **kwargs: Dict[str, Any]) -> None:
        self.kwargs = kwargs

    def generate(
        self,
        prompt_input: SerializedInput,
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
    ) -> Union[Prompt, PromptStream]:
        prompts = to_prompt_list(prompt_input)
        all_args = {
            **self.kwargs,
            "stream": stream,
            "temperature": temperature,
            "top_p": top_p,
            "n": n,
            "stop": stop,
            "max_tokens": max_tokens,
            "presence_penalty": presence_penalty,
            "frequency_penalty": frequency_penalty,
            "logit_bias": kwargs.get("logit_bias", None),
            "user": user,
            **kwargs,
        }
        all_args = {k: v for k, v in all_args.items() if v is not None}
        if "model" not in all_args:
            raise ValueError("parameter model is required")
        messages = self._to_messages(prompts)
        response = openai.ChatCompletion.create(messages=messages, **all_args)
        if "stream" in all_args and all_args["stream"]:
            return PromptStream(response, _chat_response_to_prompt_transformer)
        content = response["choices"][0]["message"]["content"]
        return prompt_output(content)

    def _to_messages(self, prompts: List[Prompt]) -> List[Dict[str, str]]:
        role_lookup = {Role.SYSTEM.value: "system", Role.AI.value: "assistant", Role.USER.value: "user"}
        return [{"role": role_lookup[p.role.value], "content": p.text} for p in prompts]

    def __call__(self, *args: Iterable[Any], **kwargs: Dict[str, Any]) -> NoReturn:
        raise TypeError(f"'{type(self).__name__}' object is not callable, did you mean to call 'generate'?")


class OpenAIText(LLM):
    """OpenAI Text API implementation for :class:`bodhilib.LLM`."""

    def __init__(self, **kwargs: Dict[str, Any]) -> None:
        self.kwargs = kwargs

    def generate(
        self,
        prompt_input: SerializedInput,
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
        **kwargs: Any,
    ) -> Union[Prompt, PromptStream]:
        prompts = to_prompt_list(prompt_input)
        prompt = self._to_prompt(prompts)
        all_args = {
            **self.kwargs,
            "stream": stream,
            "suffix": kwargs.pop("suffix", None),
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "n": n,
            "logprobs": kwargs.pop("logprobs", None),
            "echo": kwargs.pop("echo", None),
            "stop": stop,
            "presence_penalty": presence_penalty,
            "frequency_penalty": frequency_penalty,
            "best_of": kwargs.pop("best_of", None),
            "logit_bias": kwargs.get("logit_bias", None),
            "user": user,
            **kwargs,
        }
        all_args = {k: v for k, v in all_args.items() if v is not None}
        if "model" not in all_args:
            raise ValueError("parameter model is required")
        response = openai.Completion.create(prompt=prompt, **all_args)
        if "stream" in all_args and all_args["stream"]:
            return PromptStream(response, _text_response_to_prompt_transfromer)
        return _text_response_to_prompt_transfromer(response)

    def _to_prompt(self, prompts: List[Prompt]) -> str:
        return "\n".join([p.text for p in prompts])

    def __call__(self, *args: Iterable[Any], **kwargs: Dict[str, Any]) -> NoReturn:
        raise TypeError(f"'{type(self).__name__}' object is not callable, did you mean to call 'generate'?")


def _chat_response_to_prompt_transformer(response: OpenAIResponse) -> Prompt:
    result = response["choices"][0]
    content = "" if result["finish_reason"] else result["delta"]["content"]
    return prompt_output(content)


def _text_response_to_prompt_transfromer(response: OpenAIResponse) -> Prompt:
    result = response["choices"][0]["text"]
    return prompt_output(result)

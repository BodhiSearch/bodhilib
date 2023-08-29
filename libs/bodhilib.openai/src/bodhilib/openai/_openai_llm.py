"""OpenAI LLM module."""
from typing import Any, Dict, Iterable, List, NoReturn, Optional

from bodhilib.llm import LLM
from bodhilib.models import Prompt, prompt_output

import openai


class OpenAIChat(LLM):
    """OpenAI Chat API implementation for :class:`bodhilib.llm.LLM`."""

    def __init__(self, model: str, **kwargs: Dict[str, Any]) -> None:
        self.model = model
        self.kwargs = kwargs

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
    ) -> Prompt:
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
        messages = self._to_messages(prompts)
        completion = openai.ChatCompletion.create(model=self.model, messages=messages, **all_args)
        response = completion.choices[0].message["content"]
        return prompt_output(response)

    def _to_messages(self, prompts: List[Prompt]) -> List[Dict[str, str]]:
        return [{"role": p.role, "content": p.text} for p in prompts]

    def __call__(self, *args: Iterable[Any], **kwargs: Dict[str, Any]) -> NoReturn:
        raise TypeError(f"'{type(self).__name__}' object is not callable, did you mean to call 'generate'?")


class OpenAIText(LLM):
    """OpenAI Text API implementation for :class:`bodhilib.llm.LLM`."""

    def __init__(self, model: str, **kwargs: Dict[str, Any]) -> None:
        self.model = model
        self.kwargs = kwargs

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
        **kwargs: Any,
    ) -> Prompt:
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
        result = openai.Completion.create(model=self.model, prompt=prompt, **all_args)
        response = result.choices[0]["text"]
        return prompt_output(response)

    def _to_prompt(self, prompts: List[Prompt]) -> str:
        return "\n".join([p.text for p in prompts])

    def __call__(self, *args: Iterable[Any], **kwargs: Dict[str, Any]) -> NoReturn:
        raise TypeError(f"'{type(self).__name__}' object is not callable, did you mean to call 'generate'?")

"""OpenAI LLM module."""
from typing import Any, Dict, Iterable, List, NoReturn

from bodhilib.llm import LLM
from bodhilib.models import Prompt, prompt_output

import openai


class OpenAIChat(LLM):
    """OpenAI Chat API implementation for :class:`bodhilib.llm.LLM`."""

    def __init__(self, model: str, **kwargs: Dict[str, Any]) -> None:
        self.model = model
        self.kwargs = kwargs

    def _generate(self, prompts: List[Prompt], **kwargs: Dict[str, Any]) -> Prompt:
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
        messages = self._to_messages(prompts)
        completion = openai.ChatCompletion.create(model=self.model, messages=messages, **varags)
        response = completion.choices[0].message["content"]
        return prompt_output(response)

    def _to_messages(self, prompts: List[Prompt]) -> List[Dict[str, str]]:
        return [{"role": p.role, "content": p.text} for p in prompts]

    def __call__(self, *args: Iterable[Any], **kwargs: Dict[str, Any]) -> NoReturn:
        raise TypeError(f"'{type(self).__name__}' object is not callable, did you mean to call 'generate'?")


class OpenAIClassic(LLM):
    """OpenAI Classic API implementation for :class:`bodhilib.llm.LLM`."""

    def __init__(self, model: str, **kwargs: Dict[str, Any]) -> None:
        self.model = model
        self.kwargs = kwargs

    def _generate(self, prompts: List[Prompt], **kwargs: Any) -> Prompt:
        prompt = self._to_prompt(prompts)
        result = openai.Completion.create(model=self.model, prompt=prompt, **kwargs)
        response = result.choices[0]["text"]
        return prompt_output(response)

    def _to_prompt(self, prompts: List[Prompt]) -> str:
        return "\n".join([p.text for p in prompts])

    def __call__(self, *args: Iterable[Any], **kwargs: Dict[str, Any]) -> NoReturn:
        raise TypeError(f"'{type(self).__name__}' object is not callable, did you mean to call 'generate'?")

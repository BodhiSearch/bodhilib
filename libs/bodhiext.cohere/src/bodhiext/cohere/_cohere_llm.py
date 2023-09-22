"""LLM implementation for Cohere."""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from bodhilib import LLM, Prompt, PromptStream, SerializedInput, to_prompt_list, prompt_output

import cohere
from cohere.responses.generation import StreamingText


class Cohere(LLM):
    """Cohere API implementation for :class:`~bodhilib.LLM`."""

    def __init__(
        self,
        client: Optional[cohere.Client] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        **kwargs: Dict[str, Any],
    ):
        all_args = {"model": model, "api_key": api_key, **kwargs}
        self.kwargs = {k: v for k, v in all_args.items() if v is not None}

        if client:
            self.client = client
        else:
            allowed_args = [
                "api_key",
                "num_workers",
                "request_dict",
                "check_api_key",
                "client_name",
                "max_retries",
                "timeout",
                "api_url",
            ]
            args = {k: v for k, v in self.kwargs.items() if k in allowed_args}
            self.client = cohere.Client(**args)

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
        if len(prompts) == 0:
            raise ValueError("Prompt is empty")
        input = self._to_cohere_prompt(prompts)
        if input == "":
            raise ValueError("Prompt is empty")
        all_args = {
            **self.kwargs,
            "stream": stream,
            "num_generations": n,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "p": top_p,
            "k": top_k,
            "frequency_penalty": frequency_penalty,
            "presence_penalty": presence_penalty,
            "stop_sequences": stop,
            "user": user,
            **kwargs,
        }
        all_args = {k: v for k, v in all_args.items() if v is not None}
        if "model" not in all_args:
            raise ValueError("parameter model is required")

        allowed_args = [
            "prompt",
            "prompt_vars",
            "model",
            "preset",
            "num_generations",
            "max_tokens",
            "temperature",
            "k",
            "p",
            "frequency_penalty",
            "presence_penalty",
            "end_sequences",
            "stop_sequences",
            "return_likelihoods",
            "truncate",
            "logit_bias",
            "stream",
            "user",
        ]
        args = {k: v for k, v in all_args.items() if k in allowed_args}

        response = self.client.generate(input, **args)

        if "stream" in all_args and all_args["stream"]:
            return PromptStream(response, _cohere_stream_to_prompt_transformer)
        text = response.generations[0].text
        return prompt_output(text)

    def _to_cohere_prompt(self, prompts: List[Prompt]) -> str:
        return "\n".join([p.text for p in prompts])


def _cohere_stream_to_prompt_transformer(chunk: StreamingText) -> Prompt:
    return prompt_output(chunk.text)

"""LLM implementation for Cohere."""
from typing import Any, Dict, Iterable, List, Optional, Union

from bodhilib.llm import LLM
from bodhilib.models import Prompt, prompt_output

import cohere
from cohere.responses import StreamingGenerations


class Cohere(LLM):
    """Cohere API implementation for :class:`bodhilib.llm.LLM`."""

    def __init__(self, model: str, api_key: Optional[str], **kwargs: Dict[str, Any]):
        self.model = model
        self.client = cohere.Client(api_key=api_key)
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
    ) -> Union[Prompt, Iterable[Prompt]]:
        input = self._to_cohere_input(prompts)
        all_args = {
            "model": self.model,
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
            # other cohere specific args
            "end_sequences": kwargs.pop("end_sequences", None),
            "return_likelihoods": kwargs.pop("return_likelihoods", None),
            "truncate": kwargs.pop("truncate", None),
            "logit_bias": kwargs.pop("logit_bias", None),
            **kwargs,
        }
        all_args = {k: v for k, v in all_args.items() if v is not None}
        response = self.client.generate(input, **all_args)
        if "stream" in all_args and all_args["stream"]:
            return _cohere_prompt_stream(response)
        text = response.generations[0].text
        return prompt_output(text)

    def _to_cohere_input(self, prompts: List[Prompt]) -> str:
        return "\n".join([p.text for p in prompts])


def _cohere_prompt_stream(response: StreamingGenerations) -> Iterable[Prompt]:
    response_stream = iter(response)
    for chunk in response_stream:
        if chunk.is_finished:
            break
        yield prompt_output(chunk.text)

import os
from typing import Dict, List, NamedTuple

import openai

import bodhisearch
from bodhisearch.hookspecs import Provider
from bodhisearch.prompt import Prompt, PromptInput, parse_prompts


@bodhisearch.provider
def bodhisearch_get_providers() -> List[Provider]:
    return [Provider("openai", "bodhisearch", "llm", get_llm, "0.1.0")]


def get_llm(provider: str, model: str, api_key: str = None):
    if provider != "openai":
        raise ValueError(f"Unknown provider: {provider}")
    if api_key is None:
        if os.environ.get("OPENAI_API_KEY") is None:
            raise ValueError("environment variable OPENAI_API_KEY is not set")
        else:
            openai.api_key = os.environ["OPENAI_API_KEY"]
    else:
        openai.api_key = api_key
    if model.startswith("gpt"):
        return OpenAIChat(model)
    else:
        return OpenAIClassic(model)


class OpenAIChat(NamedTuple):
    model: str

    def generate(self, prompts: PromptInput):
        parsed_prompts = parse_prompts(prompts)
        completion = openai.ChatCompletion.create(
            model=self.model,
            messages=self._to_messages(parsed_prompts),
        )
        return Prompt(completion.choices[0].message["content"], role="ai")

    def _to_messages(self, prompts: List[Prompt]) -> List[Dict[str, str]]:
        return [{"role": p.role, "content": p.text} for p in prompts]

    def __call__(self, *args, **kwargs):
        raise TypeError(f"'{type(self).__name__}' object is not callable, did you mean to call 'generate'?")


class OpenAIClassic(NamedTuple):
    model: str

    def generate(self, prompts: PromptInput):
        parsed_prompts = parse_prompts(prompts)
        prompt = self._to_prompt(parsed_prompts)
        result = openai.Completion.create(model=self.model, prompt=prompt)
        return Prompt(result.choices[0]["text"], role="ai")

    def _to_prompt(self, prompts: List[Prompt]) -> str:
        return "\n".join([p.text for p in prompts])

    def __call__(self, *args, **kwargs):
        raise TypeError(f"'{type(self).__name__}' object is not callable, did you mean to call 'generate'?")

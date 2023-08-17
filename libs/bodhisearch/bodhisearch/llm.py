import abc

from bodhisearch.prompt import Prompt, PromptInput


class LLM(abc.ABC):
    @abc.abstractmethod
    def generate(self, prompts: PromptInput) -> Prompt:
        ...

import bodhiext
from bodhiext.cohere import Cohere, cohere_llm_service_builder
from bodhiext.openai import OpenAIChat, OpenAIText, openai_chat_service_builder, openai_text_service_builder

bodhiext_llms = {
    "openai_chat": {
        "service_name": "openai_chat",
        "llm_service_builder": openai_chat_service_builder,
        "model_name": "gpt-3.5-turbo",
        "llm_class": OpenAIChat,
        "version": bodhiext.openai.__version__,
    },
    "openai_text": {
        "service_name": "openai_text",
        "llm_service_builder": openai_text_service_builder,
        "model_name": "text-curie-001",
        "llm_class": OpenAIText,
        "version": bodhiext.openai.__version__,
    },
    "cohere": {
        "service_name": "cohere",
        "llm_service_builder": cohere_llm_service_builder,
        "model_name": "command",
        "llm_class": Cohere,
        "version": bodhiext.cohere.__version__,
    },
}


def explode(llm_params):  # type: ignore
    return (
        llm_params["service_name"],
        llm_params["llm_service_builder"],
        llm_params["model_name"],
        llm_params["llm_class"],
        llm_params["version"],
    )

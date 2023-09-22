import bodhiext
from bodhiext.cohere import Cohere, cohere_llm_service_builder
from bodhiext.openai import OpenAIChat, OpenAIText, openai_chat_service_builder, openai_text_service_builder
from bodhiext.qdrant import Qdrant, qdrant_service_builder

bodhiext_llms = {
    "openai_chat": {
        "service_name": "openai_chat",
        "llm_service_builder": openai_chat_service_builder,
        "model_name": "gpt-3.5-turbo",
        "llm_class": OpenAIChat,
        "publisher": "bodhiext",
        "version": bodhiext.openai.__version__,
    },
    "openai_text": {
        "service_name": "openai_text",
        "llm_service_builder": openai_text_service_builder,
        "model_name": "text-curie-001",
        "llm_class": OpenAIText,
        "publisher": "bodhiext",
        "version": bodhiext.openai.__version__,
    },
    "cohere": {
        "service_name": "cohere",
        "llm_service_builder": cohere_llm_service_builder,
        "model_name": "command",
        "llm_class": Cohere,
        "publisher": "bodhiext",
        "version": bodhiext.cohere.__version__,
    },
}

bodhiext_vector_dbs = {
    "qdrant": {
        "service_name": "qdrant",
        "vector_db_service_builder": qdrant_service_builder,
        "vector_db_class": Qdrant,
        "publisher": "bodhiext",
        "version": bodhiext.qdrant.__version__,
    }
}


def unwrap_llm(llm_params):  # type: ignore
    return (
        llm_params["service_name"],
        llm_params["llm_service_builder"],
        llm_params["model_name"],
        llm_params["llm_class"],
        llm_params["publisher"],
        llm_params["version"],
    )


def unwrap_vector_db(vector_db_params):  # type: ignore
    return (
        vector_db_params["service_name"],
        vector_db_params["vector_db_service_builder"],
        vector_db_params["vector_db_class"],
        vector_db_params["publisher"],
        vector_db_params["version"],
    )

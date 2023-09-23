import bodhiext
from bodhiext.cohere import Cohere, cohere_llm_service_builder
from bodhiext.data_loader import FileLoader, file_loader_service_builder
from bodhiext.openai import OpenAIChat, OpenAIText, openai_chat_service_builder, openai_text_service_builder
from bodhiext.qdrant import Qdrant, qdrant_service_builder

from .file_loader_helper import setup_file_loader, teardown_file_loader

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


bodhiext_data_loaders = {
    "file": {
        "service_name": "file",
        "data_loader_service_builder": file_loader_service_builder,
        "data_loader_class": FileLoader,
        "publisher": "bodhiext",
        "version": bodhiext.data_loader.__version__,
        "happypath": {
            "setup": setup_file_loader,
            "resources": ["libs/bodhitest/tmp/file_loader/test1.txt", "libs/bodhitest/tmp/file_loader/test2.txt"],
            "text": ["hello world!", "world hello!"],
            "teardown": teardown_file_loader,
        },
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


def unwrap_data_loader(data_loader_params):  # type: ignore
    return (
        data_loader_params["service_name"],
        data_loader_params["data_loader_service_builder"],
        data_loader_params["data_loader_class"],
        data_loader_params["publisher"],
        data_loader_params["version"],
    )

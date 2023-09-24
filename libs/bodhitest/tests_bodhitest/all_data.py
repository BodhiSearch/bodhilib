import bodhiext
from bodhiext.cohere import Cohere, cohere_llm_service_builder
from bodhiext.data_loader import FileLoader, file_loader_service_builder
from bodhiext.openai import OpenAIChat, OpenAIText, openai_chat_service_builder, openai_text_service_builder
from bodhiext.prompt_source import LocalDirectoryPromptSource, bodhi_prompt_source_builder
from bodhiext.qdrant import Qdrant, qdrant_service_builder
from bodhiext.sentence_transformers import SentenceTransformerEmbedder, sentence_transformer_builder
from bodhiext.splitter import TextSplitter, text_splitter_service_builder

from .file_loader_helper import setup_file_loader, teardown_file_loader

bodhiext_llms = {
    "openai_chat": {
        "service_name": "openai_chat",
        "service_type": "llm",
        "service_class": OpenAIChat,
        "publisher": "bodhiext",
        "version": bodhiext.openai.__version__,
        "service_args": {
            "model": "gpt-3.5-turbo",
        },
        "service_builder": openai_chat_service_builder,
    },
    "openai_text": {
        "service_name": "openai_text",
        "service_type": "llm",
        "service_class": OpenAIText,
        "publisher": "bodhiext",
        "version": bodhiext.openai.__version__,
        "service_args": {
            "model": "text-curie-001",
        },
        "service_builder": openai_text_service_builder,
    },
    "cohere": {
        "service_name": "cohere",
        "service_type": "llm",
        "service_class": Cohere,
        "publisher": "bodhiext",
        "version": bodhiext.cohere.__version__,
        "service_args": {
            "model": "command",
        },
        "service_builder": cohere_llm_service_builder,
    },
}

bodhiext_vector_dbs = {
    "qdrant": {
        "service_name": "qdrant",
        "service_type": "vector_db",
        "service_class": Qdrant,
        "publisher": "bodhiext",
        "version": bodhiext.qdrant.__version__,
        "service_args": {},
        "service_builder": qdrant_service_builder,
    }
}


bodhiext_data_loaders = {
    "file": {
        "service_name": "file",
        "service_type": "data_loader",
        "service_class": FileLoader,
        "publisher": "bodhiext",
        "version": bodhiext.data_loader.__version__,
        "service_args": {},
        "service_builder": file_loader_service_builder,
        "happypath": {
            "setup": setup_file_loader,
            "resources": ["libs/bodhitest/tmp/file_loader/test1.txt", "libs/bodhitest/tmp/file_loader/test2.txt"],
            "text": ["hello world!", "world hello!"],
            "teardown": teardown_file_loader,
        },
    }
}

bodhiext_splitters = {
    "text": {
        "service_name": "text_splitter",
        "service_type": "splitter",
        "service_class": TextSplitter,
        "publisher": "bodhiext",
        "version": bodhiext.splitter.__version__,
        "service_args": {"overlap": 0, "min_len": 100, "max_len": 500},
        "service_builder": text_splitter_service_builder,
    }
}

bodhiext_embedders = {
    "sentence_transformers": {
        "service_name": "sentence_transformers",
        "service_type": "embedder",
        "service_class": SentenceTransformerEmbedder,
        "publisher": "bodhiext",
        "version": bodhiext.sentence_transformers.__version__,
        "service_args": {"model": "all-MiniLM-L6-v2"},
        "service_builder": sentence_transformer_builder,
    }
}

bodhiext_prompt_sources = {
    "local_dir_prompt_source": {
        "service_name": "local_dir_prompt_source",
        "service_type": "prompt_source",
        "service_class": LocalDirectoryPromptSource,
        "publisher": "bodhiext",
        "version": bodhiext.prompt_source.__version__,
        "service_args": {},
        "service_builder": bodhi_prompt_source_builder,
    }
}

all_plugins = {
    **bodhiext_llms,
    **bodhiext_vector_dbs,
    **bodhiext_data_loaders,
    **bodhiext_splitters,
    **bodhiext_embedders,
}

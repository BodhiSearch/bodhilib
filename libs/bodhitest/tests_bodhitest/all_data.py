from typing import Any, Dict

import bodhiext
from bodhiext.data_loader import FileLoader, file_loader_service_builder
from bodhiext.prompt_source import LocalPromptSource, bodhi_prompt_source_builder
from bodhiext.splitter import TextSplitter, text_splitter_service_builder

from .file_loader_helper import setup_file_loader, teardown_file_loader

bodhiext_llms: Dict[str, Any] = {}

bodhiext_vector_dbs: Dict[str, Any] = {}


bodhiext_data_loaders = {
  "file": {
    "service_name": "file",
    "service_type": "data_loader",
    "service_class": FileLoader,
    "publisher": "bodhiext",
    "version": bodhiext.common.__version__,
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
    "version": bodhiext.common.__version__,
    "service_args": {"overlap": 0, "min_len": 100, "max_len": 500},
    "service_builder": text_splitter_service_builder,
  }
}

bodhiext_embedders: Dict[str, Any] = {}

bodhiext_prompt_sources = {
  "local_prompt_source": {
    "service_name": "local_prompt_source",
    "service_type": "prompt_source",
    "service_class": LocalPromptSource,
    "publisher": "bodhiext",
    "version": bodhiext.common.__version__,
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
  **bodhiext_prompt_sources,
}

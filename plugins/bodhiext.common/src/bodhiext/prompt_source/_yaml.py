import os
from typing import Any, Dict, List

from bodhiext.prompt_template import StringPromptTemplate
from bodhilib import PathLike, PromptTemplate
from bodhilib.logging import logger
from bodhiext.common import yaml_dump, yaml_load

def load_prompt_template_yaml(path: PathLike) -> List[PromptTemplate]:
    templates: List[PromptTemplate] = []
    if not _is_yaml(path):
        logger.debug(f"skipping parsing file for prompt templates: {path}")
        return templates

    with open(path, "r") as f:
        parsed_templates = yaml_load(f.read())
    for parsed_template in parsed_templates["templates"]:
        prompts = parsed_template.pop("prompts")
        template = StringPromptTemplate(prompts=prompts, metadata=parsed_template)
        templates.append(template)
    return templates


def dump_prompt_template_to_yaml(templates: List[StringPromptTemplate], file_path: str) -> None:
    result = []
    for template in templates:
        serialized = {**template.metadata, "prompts": [prompt.model_dump() for prompt in template.prompts]}
        serialized = ordered_dict(serialized, ["format", "tags", "prompts"])
        result.append(serialized)
    with open(file_path, "w") as f:
        output = yaml_dump({"templates": result})
        f.write(output)


def ordered_dict(data: Dict[str, Any], key_order: List[str]) -> Dict[str, Any]:
    sorted_keys = sorted(data.keys(), key=lambda x: (key_order.index(x) if x in key_order else len(key_order), x))
    return {k: data[k] for k in sorted_keys}


def _is_yaml(file: PathLike) -> bool:
    if isinstance(file, str):
        return file.endswith((".yaml", ".yml"))
    elif isinstance(file, os.PathLike):
        return file.name.endswith((".yaml", ".yml"))
    raise TypeError(f"Unsupported input type: {type(file)=}")

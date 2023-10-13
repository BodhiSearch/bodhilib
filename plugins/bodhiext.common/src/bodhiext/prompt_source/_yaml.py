from typing import Any, Dict, List

from bodhiext.prompt_template import StringPromptTemplate
from bodhilib import PromptTemplate, yaml_dump, yaml_load
from bodhilib.logging import logger


def load_prompt_template_yaml(file_path: str) -> List[PromptTemplate]:
    templates: List[PromptTemplate] = []
    if not file_path.endswith((".yml", ".yaml")):
        logger.debug(f"skipping parsing file for prompt templates: {file_path}")
        return templates

    with open(file_path, "r") as f:
        parsed_templates = yaml_load(f.read())
    for parsed_template in parsed_templates["templates"]:
        prompts = parsed_template.pop("prompts")
        template = StringPromptTemplate(**{"metadata": parsed_template, "prompts": prompts})
        templates.append(template)
    return templates


def dump_prompt_template_to_yaml(templates: List[StringPromptTemplate], file_path: str) -> None:
    result = []
    for template in templates:
        serialized = {**template.metadata, "prompts": [prompt.dict() for prompt in template.prompts]}
        serialized = ordered_dict(serialized, ["format", "tags", "prompts"])
        result.append(serialized)
    with open(file_path, "w") as f:
        output = yaml_dump({"templates": result})
        f.write(output)


def ordered_dict(data: Dict[str, Any], key_order: List[str]) -> Dict[str, Any]:
    sorted_keys = sorted(data.keys(), key=lambda x: (key_order.index(x) if x in key_order else len(key_order), x))
    return {k: data[k] for k in sorted_keys}

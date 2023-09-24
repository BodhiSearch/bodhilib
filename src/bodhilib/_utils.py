import re
from typing import Any, Dict, List

from ._models import PromptTemplate

BREAK_TEMPLATE = "+++"
BREAK_PROMPT = "---"
metadata_fields = ["tags", "format"]
metadata_field_pattern = "^" + "|".join(metadata_fields) + ":"


def parse_prompt_template(text: str) -> List[PromptTemplate]:
    """Parses a bodhilib-* template format to PromptTemplate."""
    lines = text.splitlines(keepends=True)
    result: List[PromptTemplate] = []
    prompt_template: Dict[str, Any] = {"template": []}
    metadata_section = False
    for line in lines:
        if re.match(metadata_field_pattern, line):
            field_name, field_vals = line.split(":")
            field_vals = field_vals.strip()
            if field_name == "tags":
                field_vals = field_vals.split(",")  # type: ignore
                field_vals = [val.strip() for val in field_vals]  # type: ignore
            prompt_template[field_name] = field_vals
            metadata_section = True
            continue
        if line.startswith(BREAK_PROMPT) and metadata_section:
            # gulp the line and continue
            metadata_section = False
            prompt_template["template"] = []  # reset the template content
            continue
        if line.startswith(BREAK_TEMPLATE):
            if "template" in prompt_template and prompt_template["template"]:
                result.append(_build_prompt_template(prompt_template))
            prompt_template = {"template": []}
            continue
        prompt_template["template"].append(line)
    if "template" in prompt_template and prompt_template["template"]:
        result.append(_build_prompt_template(prompt_template))
    return result


def _build_prompt_template(prompt_template: Dict[str, Any]) -> PromptTemplate:
    template = prompt_template.pop("template")
    prompt_template["template"] = "".join(template)
    if "format" not in prompt_template:
        prompt_template["format"] = "bodhilib-fstring"
    pt = PromptTemplate(**prompt_template)
    return pt

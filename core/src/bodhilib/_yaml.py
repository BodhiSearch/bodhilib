from typing import Any, Dict, List, cast

import yaml


class CustomDumper(yaml.SafeDumper):
    """Custom dumper that represents multi-line strings using '|'."""


def is_simple_string_list(lst: List[Any]) -> bool:
    return all(isinstance(item, str) and "\n" not in item for item in lst)


def represent_list(dumper, data) -> Any:  # type: ignore
    """Represents the list of strings as a single line if possible."""
    if is_simple_string_list(data):
        return dumper.represent_sequence("tag:yaml.org,2002:seq", data, flow_style=True)
    else:
        return dumper.represent_sequence("tag:yaml.org,2002:seq", data, flow_style=False)


def represent_ordered_dict(dumper, data) -> Any:  # type: ignore
    """Custom representer for dictionaries to maintain the insertion order."""
    return dumper.represent_mapping("tag:yaml.org,2002:map", data.items())


def multi_line_string_representer(dumper, data) -> Any:  # type: ignore
    """Represents multi-line strings with the '|' character."""
    if "\n" in data:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


# Add the custom representer to only the CustomSafeDumper
CustomDumper.add_representer(list, represent_list)
CustomDumper.add_representer(dict, represent_ordered_dict)
CustomDumper.add_representer(str, multi_line_string_representer)


def yaml_dump(data: Any, **kwargs) -> str:  # type: ignore
    """YAML dump function that uses the multiline friendly SafeDumper."""
    return yaml.dump(data, Dumper=CustomDumper, **kwargs)  # type: ignore


def yaml_load(data: str) -> Dict[str, Any]:
    """YAML safe load from the file content."""
    return cast(Dict[str, Any], yaml.safe_load(data))

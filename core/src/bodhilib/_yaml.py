from typing import Any

import yaml


class SafeDumper(yaml.SafeDumper):
    """Custom dumper that represents multi-line strings using '|'."""


def multi_line_string_representer(dumper, data) -> Any: # type: ignore
    """
    Represents multi-line strings with the '|' character.
    """
    if "\n" in data:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


# Add the custom representer to only the CustomSafeDumper
SafeDumper.add_representer(str, multi_line_string_representer)


def yaml_dump(data: Any, **kwargs) -> str: # type: ignore
    """YAML dump function that uses the multiline friendly SafeDumper."""
    return yaml.dump(data, Dumper=SafeDumper, **kwargs) # type: ignore

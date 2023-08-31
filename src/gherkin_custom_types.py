import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jsonschema import validate


@dataclass
class GherkinCustomTypes:
    custom_type: str
    valid_values: list[str]


def load_gherkin_custom_types(
    custom_types_path: Path, schema_path: Path
) -> list[GherkinCustomTypes]:
    """
    Load `GherkinCustomTypes` from `.json` file that matches schema.
    """
    schema = json.load(open(schema_path, "r"))
    custom_types = json.load(open(custom_types_path, "r"))

    validate_input_against_schema(custom_types, dict(schema))

    return [GherkinCustomTypes(**custom_type) for custom_type in custom_types]


def validate_input_against_schema(
    custom_types: list[dict[str, str | list[str]]], schema: dict[str, Any]
) -> None:
    """
    Wrapper for `jsonschema.validate`
    """
    validate(instance=custom_types, schema=schema)

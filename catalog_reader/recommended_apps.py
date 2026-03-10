import os
import yaml
import typing

from jsonschema import validate as json_schema_validate, ValidationError as JsonValidationError

from apps_validation.json_schema_utils import RECOMMENDED_APPS_JSON_SCHEMA
from apps_validation.utils import safe_yaml_load

from .names import RECOMMENDED_APPS_FILENAME


def retrieve_recommended_apps(catalog_location: str) -> typing.Dict[str, list]:
    try:
        with open(os.path.join(catalog_location, RECOMMENDED_APPS_FILENAME), 'r') as f:
            data = safe_yaml_load(f)
            json_schema_validate(data, RECOMMENDED_APPS_JSON_SCHEMA)
    except (FileNotFoundError, JsonValidationError, yaml.YAMLError):
        return {}
    else:
        return data

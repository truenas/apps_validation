import os
import yaml

from jsonschema import validate as json_schema_validate, ValidationError as JsonValidationError

from apps_exceptions import ValidationErrors
from catalog_reader.names import RECOMMENDED_APPS_FILENAME

from .json_schema_utils import RECOMMENDED_APPS_JSON_SCHEMA
from .utils import safe_yaml_load


def validate_recommended_apps_file(catalog_location: str) -> None:
    verrors = ValidationErrors()
    try:
        with open(os.path.join(catalog_location, RECOMMENDED_APPS_FILENAME), 'r') as f:
            data = safe_yaml_load(f)
        json_schema_validate(data, RECOMMENDED_APPS_JSON_SCHEMA)
    except FileNotFoundError:
        return
    except yaml.YAMLError:
        verrors.add(RECOMMENDED_APPS_FILENAME, 'Must be a valid yaml file')
    except JsonValidationError as e:
        verrors.add(RECOMMENDED_APPS_FILENAME, f'Invalid format specified: {e}')

    verrors.check()

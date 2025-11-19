import os
import yaml

from jsonschema import validate as json_schema_validate, ValidationError as JsonValidationError

from apps_exceptions import ValidationErrors
from catalog_reader.names import DEPRECATED_APPS_FILENAME

from .json_schema_utils import DEPRECATED_APPS_SCHEMA


def validate_deprecated_apps(app_dir_path: str, schema: str, verrors: ValidationErrors):
    deprecated_apps_file_path = os.path.join(app_dir_path, DEPRECATED_APPS_FILENAME)

    try:
        with open(deprecated_apps_file_path, 'r') as f:
            data = yaml.safe_load(f.read())
            json_schema_validate(data, DEPRECATED_APPS_SCHEMA)
    except FileNotFoundError:
        return
    except yaml.YAMLError:
        verrors.add(f'{schema}.{DEPRECATED_APPS_FILENAME}', 'Invalid yaml format')
    except JsonValidationError as e:
        verrors.add(
            f'{schema}.{DEPRECATED_APPS_FILENAME}',
            f'Invalid format specified: {e}'
        )

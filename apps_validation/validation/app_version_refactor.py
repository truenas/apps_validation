import os
import yaml

from typing import Optional

from jsonschema import validate as json_schema_validate, ValidationError as JsonValidationError

from apps_validation.exceptions import ValidationErrors

from .json_schema_utils import APP_METADATA_JSON_SCHEMA


def validate_app_version_file(
    verrors: ValidationErrors, app_version_path: str, schema: str, item_name: str, version_name: Optional[str] = None,
    train_name: Optional[str] = None,
) -> ValidationErrors:
    if not os.path.exists(app_version_path):
        verrors.add(
            schema, f'App version file {app_version_path!r} does not exist'
        )
        return verrors

    with open(app_version_path, 'r') as f:
        try:
            app_config = yaml.safe_load(f.read())
        except yaml.YAMLError:
            verrors.add(schema, 'Must be a valid yaml file')
            return verrors

    try:
        json_schema_validate(app_config, APP_METADATA_JSON_SCHEMA)
    except JsonValidationError as e:
        verrors.add(schema, f'Failed to validate app version file: {e.message}')
        return verrors

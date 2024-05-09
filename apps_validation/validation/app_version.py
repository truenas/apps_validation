import os
import yaml

from typing import Optional

from jsonschema import validate as json_schema_validate, ValidationError as JsonValidationError

from apps_validation.exceptions import ValidationErrors

from .json_schema_utils import APP_METADATA_JSON_SCHEMA
from .scale_version import validate_min_max_version_values


def validate_app_version_file(
    verrors: ValidationErrors, app_version_path: str, schema: str, item_name: str, version_name: Optional[str] = None,
    train_name: Optional[str] = None,
) -> ValidationErrors:
    if not os.path.exists(app_version_path):
        verrors.add(schema, 'Missing app version file')
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

    if app_config.get('name') != item_name:
        verrors.add(f'{schema}.item_name', 'Item name not correctly set in "app.yaml"')

    if app_config.get('annotations'):
        validate_min_max_version_values(app_config['annotations'], verrors, schema)

    if version_name is not None and app_config['version'] != version_name:
        verrors.add(f'{schema}.version', 'Version name does not match with the version name in the app version file')

    if train_name is not None and app_config['train'] != train_name:
        verrors.add(f'{schema}.train', 'Train name does not match with the train name in the app version file')

    return verrors

import os
import json
import yaml

from jsonschema import validate as json_schema_validate, ValidationError as JsonValidationError

from apps_ci.names import CACHED_VERSION_FILE_NAME
from apps_exceptions import ValidationErrors

from .json_schema_utils import APP_ITEM_JSON_SCHEMA
from .validate_app_version import validate_catalog_item_version_data, validate_catalog_item_version


def validate_catalog_item(catalog_item_path: str, schema: str, train_name: str, validate_versions: bool = True):
    # We should ensure that each catalog item has at least 1 version available
    # Also that we have item.yaml present
    verrors = ValidationErrors()
    item_name = os.path.join(catalog_item_path)
    files = []
    versions = []

    if not os.path.isdir(catalog_item_path):
        verrors.add(schema, 'Catalog item must be a directory')
    verrors.check()

    for file_dir in os.listdir(catalog_item_path):
        complete_path = os.path.join(catalog_item_path, file_dir)
        if os.path.isdir(complete_path):
            versions.append(complete_path)
        else:
            files.append(file_dir)

    if not versions:
        verrors.add(f'{schema}.versions', f'No versions found for {item_name} item.')

    if 'item.yaml' not in files:
        verrors.add(f'{schema}.item', 'Item configuration (item.yaml) not found')
    else:
        with open(os.path.join(catalog_item_path, 'item.yaml'), 'r') as f:
            item_config = yaml.safe_load(f.read())

        try:
            json_schema_validate(item_config, APP_ITEM_JSON_SCHEMA)
        except JsonValidationError as e:
            verrors.add(f'{schema}.item_config', f'Invalid format specified for item configuration: {e}')

    cached_version_file_path = os.path.join(catalog_item_path, CACHED_VERSION_FILE_NAME)
    if os.path.exists(cached_version_file_path):
        try:
            with open(cached_version_file_path, 'r') as f:
                validate_catalog_item_version_data(
                    json.loads(f.read()), f'{schema}.{CACHED_VERSION_FILE_NAME}', verrors
                )
        except json.JSONDecodeError:
            verrors.add(
                f'{schema}.{CACHED_VERSION_FILE_NAME}', f'{CACHED_VERSION_FILE_NAME!r} is not a valid json file'
            )

    for version_path in (versions if validate_versions else []):
        try:
            validate_catalog_item_version(
                version_path, f'{schema}.versions.{os.path.basename(version_path)}', train_name=train_name,
            )
        except ValidationErrors as e:
            verrors.extend(e)

    verrors.check()

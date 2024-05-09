import json
import pathlib
import os

from apps_validation.ci.names import CACHED_VERSION_FILE_NAME
from apps_validation.exceptions import ValidationErrors

from .validate_app_version import validate_catalog_item_version_data, validate_catalog_item_version
from .utils import validate_key_value_types


def validate_catalog_item(catalog_item_path: str, schema: str, train_name: str, validate_versions: bool = True):
    # We should ensure that each catalog item has at least 1 version available
    # Also that we have item.yaml present
    verrors = ValidationErrors()
    item_name = os.path.join(catalog_item_path)
    versions_dir_exist = False
    try:
        for version_path in pathlib.Path(catalog_item_path).iterdir():
            if validate_versions and version_path.is_dir():
                versions_dir_exist = True
                try:
                    validate_catalog_item_version(
                        version_path.as_posix(),
                        f'{schema}.versions.{version_path.name}',
                        train_name=train_name,
                    )
                except ValidationErrors as e:
                    verrors.extend(e)
    except NotADirectoryError:
        verrors.add(schema, f'{catalog_item_path!r} must be a directory')
    except FileNotFoundError:
        verrors.add(schema, f'{catalog_item_path!r} not found')
    else:
        if not versions_dir_exist:
            verrors.add(f'{schema}.versions', f'No versions found for {item_name} item.')

    try:
        required_yaml_file = 'item.yaml'
        with open(os.path.join(catalog_item_path, required_yaml_file), 'r') as f:
            validate_key_value_types(
                f.read(),
                (('categories', list), ('tags', list, False), ('screenshots', list, False)),
                verrors,
                f'{schema}.item_config'
            )
    except FileNotFoundError:
        verrors.add(f'{schema}.item_config', f'Missing yaml file ({required_yaml_file})')

    verrors.check()

    cached_version_file_path = os.path.join(catalog_item_path, CACHED_VERSION_FILE_NAME)
    schema_str = f'{schema}.{CACHED_VERSION_FILE_NAME}'
    try:
        with open(cached_version_file_path, 'r') as f:
            validate_catalog_item_version_data(
                json.loads(f.read()), f'{schema}.{CACHED_VERSION_FILE_NAME}', verrors
            )
    except FileNotFoundError:
        verrors.add(schema_str, f'{CACHED_VERSION_FILE_NAME!r} not found')
    except json.JSONDecodeError:
        verrors.add(schema_str, f'{CACHED_VERSION_FILE_NAME!r} is not a valid json file')

    verrors.check()

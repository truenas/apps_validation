import os
import pathlib

import yaml
from jsonschema import validate as json_schema_validate
from semantic_version import Version

from .names import TO_KEEP_VERSIONS


DEV_DIRECTORY_RELATIVE_PATH = 'ix-dev'
OPTIONAL_METADATA_FILES = ['upgrade_info.json', 'upgrade_strategy', TO_KEEP_VERSIONS]
REQUIRED_METADATA_FILES = ['item.yaml']
REQUIRED_VERSIONS_JSON_SCHEMA = {
    'type': 'array',
    'items': {
        'type': 'string',
        'pattern': '[0-9]+.[0-9]+.[0-9]+'
    }
}


def get_app_version(app_path: str) -> str:
    # This assumes that file exists and version is specified and is good
    with open(os.path.join(app_path, 'app.yaml'), 'r') as f:
        return yaml.safe_load(f.read())['version']


def get_ci_development_directory(catalog_path: str) -> str:
    return os.path.join(catalog_path, DEV_DIRECTORY_RELATIVE_PATH)


def version_has_been_bumped(app_path: str, new_version: str) -> bool:
    versions = list()
    try:
        for version in filter(lambda x: x.is_dir(), pathlib.Path(app_path).iterdir()):
            versions.append(Version(version.name))
        versions.sort()
        return not versions or Version(new_version) > versions[-1]
    except (FileNotFoundError, NotADirectoryError):
        # why return a different type and not just an empty list?
        return True


def get_to_keep_versions(app_dir_path: str) -> list:
    required_version_path = os.path.join(app_dir_path, TO_KEEP_VERSIONS)
    if not os.path.exists(required_version_path):
        return []

    with open(required_version_path, 'r') as f:
        data = yaml.safe_load(f.read())
        json_schema_validate(data, REQUIRED_VERSIONS_JSON_SCHEMA)
    return data

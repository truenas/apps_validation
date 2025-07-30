import os
import typing


LIBRARY_HASHES_FILENAME = 'hashes.yaml'
RECOMMENDED_APPS_FILENAME = 'recommended_apps.yaml'
TO_KEEP_VERSIONS = 'to_keep_versions.yaml'


def get_app_library_dir_name_from_version(version: str) -> str:
    return f'v{version.replace(".", "_")}'


def get_base_library_dir_name_from_version(version: typing.Optional[str]) -> str:
    return f'base_v{version.replace(".", "_")}' if version else ''


def get_library_hashes_path(library_path: str) -> str:
    return os.path.join(library_path, LIBRARY_HASHES_FILENAME)


def get_library_path(catalog_path: str) -> str:
    return os.path.join(catalog_path, 'library')

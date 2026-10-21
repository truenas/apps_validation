import os


# Unversioned source of an app's own library in the dev directory,
# published as templates/library/<train>/<app>/v<version>
APP_LIBRARY_SOURCE_DIR = 'lib'
DEPRECATED_APPS_FILENAME = 'deprecations.yaml'
LIBRARY_HASHES_FILENAME = 'hashes.yaml'
RECOMMENDED_APPS_FILENAME = 'recommended_apps.yaml'
TO_KEEP_VERSIONS = 'to_keep_versions.yaml'


def get_app_library_dir_name_from_version(version: str) -> str:
    return f'v{version.replace(".", "_")}'


def get_base_library_dir_name_from_version(version: str | None) -> str:
    return f'base_v{version.replace(".", "_")}' if version else ''


def get_library_hashes_path(library_path: str) -> str:
    return os.path.join(library_path, LIBRARY_HASHES_FILENAME)


def get_library_path(catalog_path: str) -> str:
    return os.path.join(catalog_path, 'library')

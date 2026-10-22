import contextlib
import os
import pathlib
import re
import shutil
import yaml

from apps_exceptions import CatalogDoesNotExist, ValidationErrors
from apps_validation.utils import safe_yaml_load
from .dev_directory import get_ci_development_directory
from .hash_utils import EXCLUDED_NAMES, get_hash_of_directory
from .names import (
    APP_LIBRARY_SOURCE_DIR, get_app_library_dir_name_from_version, get_base_library_dir_name_from_version,
    get_library_path, get_library_hashes_path,
)


RE_VERSION = re.compile(r'^\d+.\d+\.\d+$')


def get_library_hashes(library_path: str) -> dict:
    """
    This reads from library hashes file and returns the hashes
    """
    with contextlib.suppress(FileNotFoundError, yaml.YAMLError):
        with open(get_library_hashes_path(library_path), 'r') as f:
            data: dict = safe_yaml_load(f)
            return data
    return {}


def get_hashes_of_base_lib_versions(catalog_path: str) -> dict:
    library_path = get_library_path(catalog_path)
    library_dir = pathlib.Path(library_path)
    hashes = {}
    for lib_entry in library_dir.iterdir():
        if not lib_entry.is_dir() or not RE_VERSION.match(lib_entry.name):
            continue

        hashes[lib_entry.name] = get_hash_of_directory(os.path.join(library_path, lib_entry.name))

    return hashes


def copy_app_libraries(catalog_path: str, app_path: str, destination_path: str | None = None) -> None:
    """
    Copy the base library the app uses from the catalog library and the app library from its unversioned
    source to the paths the renderer imports them from, templates/library/base_v<lib_version> and
    templates/library/<train>/<app>/v<version> of destination_path (the app itself by default).
    Copies already there are replaced, so they never outlive a version or library change.
    """
    destination_path = destination_path or app_path
    with open(os.path.join(app_path, 'app.yaml'), 'r') as f:
        app_config = safe_yaml_load(f)

    lib_version = app_config.get('lib_version')
    base_lib_path = os.path.join(get_library_path(catalog_path), lib_version or '')
    if lib_version and not os.path.isdir(base_lib_path):
        verrors = ValidationErrors()
        verrors.add('lib_version', f'Library version {lib_version!r} of {app_config["name"]!r} does not exist')
        verrors.check()

    library_path = pathlib.Path(destination_path, 'templates/library')
    if library_path.is_dir():
        for old_copy in library_path.iterdir():
            if old_copy.is_dir() and (old_copy.name.startswith('base_') or old_copy.name == app_config['train']):
                shutil.rmtree(old_copy)

    if lib_version:
        shutil.copytree(
            base_lib_path, library_path / get_base_library_dir_name_from_version(lib_version),
            ignore=shutil.ignore_patterns(*EXCLUDED_NAMES),
        )

    app_lib_path = os.path.join(app_path, APP_LIBRARY_SOURCE_DIR)
    if os.path.isdir(app_lib_path):
        shutil.copytree(
            app_lib_path,
            library_path / app_config['train'] / app_config['name'] /
            get_app_library_dir_name_from_version(app_config['version']),
            ignore=shutil.ignore_patterns(*EXCLUDED_NAMES),
        )


def prepare_dev_apps_libraries(catalog_path: str, to_prepare_apps: dict[str, list[str]] | None = None) -> None:
    """
    Copy the libraries into the dev directory apps, all of them or only to_prepare_apps ({train: [app, ...]}),
    so they can be rendered and validated. The copies are not to be committed, publish makes its own
    """
    if not os.path.exists(catalog_path):
        raise CatalogDoesNotExist(catalog_path)

    verrors = ValidationErrors()
    dev_directory = get_ci_development_directory(catalog_path)
    with os.scandir(dev_directory) as trains:
        for train in sorted(trains, key=lambda e: e.name):
            if not train.is_dir() or (to_prepare_apps is not None and train.name not in to_prepare_apps):
                continue

            with os.scandir(train.path) as apps:
                for app in sorted(apps, key=lambda e: e.name):
                    if to_prepare_apps is not None and app.name not in to_prepare_apps[train.name]:
                        continue
                    if not os.path.isfile(os.path.join(app.path, 'app.yaml')):
                        continue

                    try:
                        copy_app_libraries(catalog_path, app.path)
                    except ValidationErrors as e:
                        verrors.add_child(f'dev.{train.name}.{app.name}', e)

    verrors.check()

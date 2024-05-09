import pathlib
import os

import yaml
from jsonschema import ValidationError as JsonValidationError

from apps_validation.exceptions import ValidationErrors
from catalog_reader.dev_directory import (
    get_app_version, get_ci_development_directory, get_to_keep_versions, REQUIRED_METADATA_FILES,
    version_has_been_bumped,
)
from catalog_reader.names import UPGRADE_STRATEGY_FILENAME, TO_KEEP_VERSIONS

from .app_version import validate_app_version_file
from .validate_app_version import validate_catalog_item_version


def validate_dev_directory_structure(catalog_path: str, to_check_apps: dict) -> None:
    verrors = ValidationErrors()
    try:
        for i in pathlib.Path(get_ci_development_directory(catalog_path)).iterdir():
            if i.is_dir() and i.name in to_check_apps:
                validate_train(catalog_path, i.as_posix(), f'dev.{i.name}', to_check_apps[i.name])
    except (FileNotFoundError, NotADirectoryError):
        return

    verrors.check()


def validate_train(catalog_path: str, train_path: str, schema: str, to_check_apps: list) -> None:
    verrors = ValidationErrors()
    train_name = os.path.basename(train_path)
    for app_path in pathlib.Path(train_path).iterdir():
        if not app_path.is_dir():
            continue

        app_name = app_path.name
        if app_name not in to_check_apps:
            continue

        try:
            validate_app(app_path.as_posix(), f'{schema}.{app_name}', train_name)
        except ValidationErrors as ve:
            verrors.extend(ve)
        else:
            published_train_app_path = os.path.join(catalog_path, train_name, app_name)
            try:
                if not version_has_been_bumped(published_train_app_path, get_app_version(app_path.name)):
                    verrors.add(
                        f'{schema}.{app_name}.version',
                        'Version must be bumped as app has been changed but version has not been updated'
                    )
            except FileNotFoundError:
                # The application is new and we are good
                continue

        verrors.check()


def validate_upgrade_strategy(app_path: str, schema: str, verrors: ValidationErrors):
    upgrade_strategy_path = os.path.join(app_path, UPGRADE_STRATEGY_FILENAME)
    try:
        if not os.access(upgrade_strategy_path, os.X_OK):
            verrors.add(schema, f'{upgrade_strategy_path!r} is not executable')
    except FileNotFoundError:
        pass


def validate_app(app_dir_path: str, schema: str, train_name: str) -> None:
    app_name = os.path.basename(app_dir_path)
    chart_version_path = os.path.join(app_dir_path, 'app.yaml')
    verrors = validate_app_version_file(ValidationErrors(), chart_version_path, schema, app_name)
    validate_keep_versions(app_dir_path, app_name, verrors)
    verrors.check()

    validate_catalog_item_version(
        app_dir_path, schema, get_app_version(app_dir_path), app_name, True, train_name=train_name,
    )

    # TODO: Stop using globally defined mutable objects
    total_num_of_required_files = len(REQUIRED_METADATA_FILES)
    total_num_of_required_files_found = 0
    for i in pathlib.Path(app_dir_path).iterdir():
        if total_num_of_required_files_found == total_num_of_required_files:
            break
        elif i.is_file() and i.name in REQUIRED_METADATA_FILES:
            total_num_of_required_files_found += 1

    if total_num_of_required_files_found != total_num_of_required_files:
        verrors.add(
            f'{schema}.required_files',
            f'All of the following files must exist: {", ".join(REQUIRED_METADATA_FILES)!r}'
        )
    validate_upgrade_strategy(app_dir_path, f'{schema}.{UPGRADE_STRATEGY_FILENAME}', verrors)
    verrors.check()


def validate_keep_versions(app_dir_path: str, schema: str, verrors: ValidationErrors):
    try:
        get_to_keep_versions(app_dir_path)
    except yaml.YAMLError:
        verrors.add(f'{schema}.to_keep_versions', 'Invalid yaml format')
    except JsonValidationError:
        verrors.add(
            f'{schema}.to_keep_versions.yaml',
            f'Invalid json schema {TO_KEEP_VERSIONS} must contain list of required versions'
        )

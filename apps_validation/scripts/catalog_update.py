import argparse
import pathlib
import contextlib
import json
import os
import shutil
import typing
from collections import defaultdict

from jsonschema import validate as json_schema_validate, ValidationError as JsonValidationError

from apps_validation.ci.names import CACHED_CATALOG_FILE_NAME, CACHED_VERSION_FILE_NAME
from apps_validation.exceptions import ValidationErrors
from apps_validation.validation.json_schema_utils import CATALOG_JSON_SCHEMA
from apps_validation.validation.validate_app_version import validate_catalog_item_version_data
from catalog_reader.catalog import retrieve_train_names, retrieve_trains_data, get_apps_in_trains
from catalog_reader.dev_directory import (
    get_app_version, get_ci_development_directory, get_to_keep_versions, OPTIONAL_METADATA_FILES,
    REQUIRED_METADATA_FILES, version_has_been_bumped,
)
from catalog_reader.train_utils import get_train_path


def get_trains(location: str) -> typing.Tuple[dict, dict]:
    preferred_trains: list = []
    trains_to_traverse = retrieve_train_names(get_train_path(location))
    catalog_data = {}
    versions_data = {}
    for train_name, train_data in retrieve_trains_data(
        get_apps_in_trains(trains_to_traverse, location), location, preferred_trains, trains_to_traverse
    )[0].items():
        catalog_data[train_name] = {}
        versions_data[train_name] = {}
        for app_name, app_data in train_data.items():
            catalog_data[train_name][app_name] = {}
            versions_data[train_name][app_name] = {}
            for k, v in app_data.items():
                if k == 'versions':
                    versions_data[train_name][app_name][k] = v
                else:
                    catalog_data[train_name][app_name][k] = v

    return catalog_data, versions_data


def validate_train_data(train_data):
    verrors = ValidationErrors()
    try:
        json_schema_validate(train_data, CATALOG_JSON_SCHEMA)
    except (json.JSONDecodeError, JsonValidationError) as e:
        verrors.add(
            'catalog_json',
            f'Failed to validate contents of train data: {e!r}'
        )
    verrors.check()


def validate_versions_data(versions_data):
    verrors = ValidationErrors()
    for train_name, train_data in versions_data.items():
        for app_name, app_version_data in train_data.items():
            validate_catalog_item_version_data(app_version_data['versions'], f'{train_name}.{app_name}', verrors)
    verrors.check()


def get_apps_to_publish(catalog_path: str) -> dict:
    ci_dev_dir = get_ci_development_directory(catalog_path)
    to_publish_apps = defaultdict(list)
    for train_path in filter(lambda x: x.is_dir(), pathlib.Path(ci_dev_dir).iterdir()):
        train_name = train_path.name
        for app_path in filter(lambda x: x.is_dir(), train_path.iterdir()):
            app_name = app_path.name
            app_current_version = get_app_version(app_path.as_posix())
            if version_has_been_bumped(os.path.join(catalog_path, train_name, app_name), app_current_version):
                to_publish_apps[train_name].append({'name': app_name, 'version': app_current_version})

    return to_publish_apps


def publish_updated_apps(catalog_path: str) -> None:
    ci_dev_directory = get_ci_development_directory(catalog_path)
    if not os.path.isdir(ci_dev_directory):
        return

    for train_name, apps in get_apps_to_publish(catalog_path).items():
        dev_train_path = os.path.join(ci_dev_directory, train_name)
        publish_train_path = os.path.join(get_train_path(catalog_path), train_name)
        os.makedirs(publish_train_path, exist_ok=True)

        for app in apps:
            # TODO: This should account for the new library structure
            app_name, app_version = app['name'], app['version']
            dev_app_path = os.path.join(dev_train_path, app_name)
            publish_app_path = os.path.join(publish_train_path, app_name)
            publish_app_version_path = os.path.join(publish_app_path, app_version)
            required_versions = get_to_keep_versions(dev_app_path)
            os.makedirs(publish_app_path, exist_ok=True)

            dev_item_yaml_path = os.path.join(dev_app_path, 'item.yaml')
            publish_item_yaml_path = os.path.join(publish_app_path, 'item.yaml')
            shutil.copy(dev_item_yaml_path, publish_item_yaml_path)
            shutil.copytree(dev_app_path, publish_app_version_path)

            for file_name in OPTIONAL_METADATA_FILES + REQUIRED_METADATA_FILES:
                with contextlib.suppress(OSError):
                    os.unlink(os.path.join(publish_app_version_path, file_name))

            ix_values_path = os.path.join(publish_app_version_path, 'ix_values.yaml')
            values_path = os.path.join(publish_app_version_path, 'values.yaml')
            if not os.path.exists(ix_values_path) and os.path.exists(values_path):
                shutil.move(values_path, ix_values_path)

            for version in pathlib.Path(publish_app_path).iterdir():
                if all((
                    version.is_dir(),
                    version.name in required_versions
                )):
                    continue

                if version.name != app_version:
                    shutil.rmtree(version.as_posix())

            print(
                f'[\033[92mOK\x1B[0m]\tPublished {app_name!r} having {app_version!r} version '
                f'to {train_name!r} train successfully!'
            )


def update_catalog_file(location: str) -> None:
    catalog_file_path = os.path.join(location, CACHED_CATALOG_FILE_NAME)
    catalog_data, versions_data = get_trains(location)
    validate_train_data(catalog_data)
    validate_versions_data(versions_data)

    with open(catalog_file_path, 'w') as f:
        f.write(json.dumps(catalog_data, indent=4))

    print(f'[\033[92mOK\x1B[0m]\tUpdated {catalog_file_path!r} successfully!')

    for train_name, train_data in versions_data.items():
        for app_name, app_data in train_data.items():
            version_path = os.path.join(get_train_path(location), train_name, app_name, CACHED_VERSION_FILE_NAME)
            with open(version_path, 'w') as f:
                f.write(json.dumps(app_data['versions'], indent=4))

            print(f'[\033[92mOK\x1B[0m]\tUpdated {version_path!r} successfully!')


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='sub-command help', dest='action')

    publish_setup = subparsers.add_parser('publish', help='Publish apps of TrueNAS catalog')
    publish_setup.add_argument('--path', help='Specify path of TrueNAS catalog')

    parser_setup = subparsers.add_parser('update', help='Update TrueNAS catalog')
    parser_setup.add_argument('--path', help='Specify path of TrueNAS catalog')

    args = parser.parse_args()
    if args.action == 'publish':
        publish_updated_apps(args.path)
    elif args.action == 'update':
        update_catalog_file(args.path)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()

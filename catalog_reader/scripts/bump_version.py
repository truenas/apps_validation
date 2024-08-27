#!/usr/bin/env python
import argparse
import os
import pathlib
import yaml

from apps_exceptions import AppDoesNotExist, ValidationErrors
from catalog_reader.version_bump import is_valid_bump_type, bump_version, rename_versioned_dir


def update_app_version(app_path: str, bump_type: str) -> None:
    if not os.path.exists(app_path):
        raise AppDoesNotExist(app_path)

    verrors = ValidationErrors()
    app_dir = pathlib.Path(app_path)
    app_metadata_file = app_dir / 'app.yaml'
    if not app_metadata_file.is_file():
        verrors.add('app_metadata', 'app.yaml file is missing')

    verrors.check()

    with open(str(app_metadata_file), 'r') as f:
        app_config = yaml.safe_load(f.read())

    if not is_valid_bump_type(bump_type):
        verrors.add('app_metadata', f'Invalid bump type {bump_type!r}')

    verrors.check()

    old_version = app_config["version"]
    app_config["version"] = bump_version(old_version, bump_type)
    rename_versioned_dir(old_version, app_config['version'], app_dir.parent.name, app_dir)

    with open(str(app_metadata_file), 'w') as f:
        f.write(yaml.safe_dump(app_config))

    print(
        f'[\033[92mOK\x1B[0m]\tUpdated app {app_dir.name!r} version from {old_version!r} to {app_config["version"]!r}'
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', help='Specify path of the app to be updated')
    parser.add_argument('--bump', help='Bump type for app that the hash was updated')

    args = parser.parse_args()
    if not args.path or not args.bump:
        parser.print_help()
    else:
        update_app_version(args.path, args.bump)


if __name__ == '__main__':
    main()

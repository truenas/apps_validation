#!/usr/bin/env python
import argparse
import os
import pathlib
import yaml

from apps_ci.images_info import is_main_dep
from apps_ci.version_bump import map_renovate_bump_type, bump_version, rename_versioned_dir
from apps_exceptions import AppDoesNotExist, ValidationErrors


def update_app_version(app_path: str, bump_type: str, dep_name: str, dep_version: str) -> None:
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

    if dep_name and dep_version and is_main_dep(app_dir, dep_name):
        app_config['app_version'] = dep_version
    if bump_type:
        old_version = app_config['version']
        app_config['version'] = bump_version(old_version, bump_type)
        rename_versioned_dir(old_version, app_config['version'], app_dir.parent.name, app_dir)

    with open(str(app_metadata_file), 'w') as f:
        f.write(yaml.safe_dump(app_config))

    print(
        f'[\033[92mOK\x1B[0m]\tUpdated app {app_dir.name!r} version from {old_version!r} to {app_config["version"]!r}'
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', help='Specify path of the app to be updated')
    parser.add_argument(
        '--bump', type=map_renovate_bump_type,
        help='Version bump type for app that the hash was updated'
    )
    parser.add_argument('--dep-name', help='Name of the dependency')
    parser.add_argument('--dep-version', type=str, help='Version of the dependency')

    args = parser.parse_args()
    if not args.path or not args.bump:
        parser.print_help()
    else:
        update_app_version(args.path, args.bump, args.dep_name, args.dep_version)


if __name__ == '__main__':
    main()

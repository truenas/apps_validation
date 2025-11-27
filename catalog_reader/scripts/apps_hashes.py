#!/usr/bin/env python
import argparse
import os
import pathlib
import shutil
import yaml

from apps_ci.version_bump import bump_version, rename_versioned_dir
from apps_exceptions import CatalogDoesNotExist, ValidationErrors
from catalog_reader.dev_directory import get_ci_development_directory
from catalog_reader.library import get_hashes_of_base_lib_versions
from catalog_reader.names import get_library_path, get_library_hashes_path, get_base_library_dir_name_from_version


def update_catalog_hashes(
    catalog_path: str,
    bump_type: str | None = None,
    train_name: str | None = None,
    app_name: str | None = None,
) -> None:
    if not os.path.exists(catalog_path):
        raise CatalogDoesNotExist(catalog_path)

    verrors = ValidationErrors()
    if (train_name and not app_name) or (app_name and not train_name):
        verrors.add('app_train', 'Both --train and --app must be specified together')

    library_dir = pathlib.Path(get_library_path(catalog_path))
    if not library_dir.exists():
        verrors.add('library', 'Library directory is missing')

    verrors.check()

    hashes = get_hashes_of_base_lib_versions(catalog_path)
    hashes_file_path = get_library_hashes_path(get_library_path(catalog_path))
    with open(hashes_file_path, 'w') as f:
        yaml.safe_dump(hashes, f)

    print(f'[\033[92mOK\x1B[0m]\tGenerated hashes for library versions at {hashes_file_path!r}')

    dev_directory = pathlib.Path(get_ci_development_directory(catalog_path))
    if not dev_directory.is_dir():
        return
    elif not hashes:
        print('[\033[92mOK\x1B[0m]\tNo hashes found for library versions, skipping updating apps hashes')
        return

    is_single_app = train_name and app_name
    for train_dir in dev_directory.iterdir():
        if not train_dir.is_dir():
            continue

        if is_single_app and train_dir.name != train_name:
            continue

        for app_dir in train_dir.iterdir():
            if not app_dir.is_dir():
                continue

            if is_single_app and app_dir.name != app_name:
                continue

            app_metadata_file = app_dir / 'app.yaml'
            if not app_metadata_file.is_file():
                continue

            with open(str(app_metadata_file), 'r') as f:
                app_config = yaml.safe_load(f.read())

            if (lib_version := app_config.get('lib_version')) and lib_version not in hashes:
                print(
                    f'[\033[93mWARN\x1B[0m]\tLibrary version {lib_version!r} not found in hashes, '
                    f'skipping updating {app_dir.name!r} in {train_dir.name} train'
                )
                continue

            base_lib_name = get_base_library_dir_name_from_version(lib_version)
            app_lib_dir = app_dir / 'templates/library'
            app_lib_dir.mkdir(exist_ok=True, parents=True)

            # Remove all old library versions
            for old_lib_dir in app_lib_dir.iterdir():
                if old_lib_dir.is_dir() and old_lib_dir.name.startswith("base_"):
                    shutil.rmtree(old_lib_dir.as_posix(), ignore_errors=True)

            app_base_lib_dir = app_lib_dir / base_lib_name
            catalog_base_lib_dir_path = os.path.join(library_dir.as_posix(), lib_version)
            shutil.copytree(catalog_base_lib_dir_path, app_base_lib_dir.as_posix())

            old_version = app_config['version']
            if bump_type and app_config['lib_version_hash'] != hashes[lib_version]:
                app_config['version'] = bump_version(old_version, bump_type)
                rename_versioned_dir(old_version, app_config['version'], train_dir.name, app_dir)

            app_config['lib_version_hash'] = hashes[lib_version]
            with open(str(app_metadata_file), 'w') as f:
                f.write(yaml.safe_dump(app_config))

            message = f'[\033[92mOK\x1B[0m]\tUpdated library hash for {app_dir.name!r} in {train_dir.name}'
            if bump_type:
                message += f' and bumped version from {old_version!r} to {app_config["version"]!r}'
            print(message)

            if is_single_app:
                return

    if is_single_app:
        verrors.add('app', f'App {app_name!r} not found in train {train_name!r}')
        verrors.check()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', help='Specify path of TrueNAS catalog')
    parser.add_argument(
        '--bump', type=str, choices=('major', 'minor', 'patch'), required=False,
        help='Version bump type for app that the hash was updated'
    )
    parser.add_argument(
        '--train', type=str, required=False,
        help='Specify a train name to filter apps'
    )
    parser.add_argument(
        '--app', type=str, required=False,
        help='Specify a single app name to update instead of updating all apps'
    )

    args = parser.parse_args()
    if not args.path:
        parser.print_help()
    else:
        update_catalog_hashes(args.path, args.bump, args.train, args.app)


if __name__ == '__main__':
    main()

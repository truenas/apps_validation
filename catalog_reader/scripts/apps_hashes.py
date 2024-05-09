#!/usr/bin/env python
import argparse
import os
import pathlib
import yaml

from apps_validation.exceptions import CatalogDoesNotExist, ValidationErrors
from catalog_reader.library import get_hashes_of_base_lib_versions
from catalog_reader.names import get_library_path, get_library_hashes_path


def update_catalog_hashes(catalog_path: str) -> None:
    if not os.path.exists(catalog_path):
        raise CatalogDoesNotExist(catalog_path)

    verrors = ValidationErrors()
    library_dir = pathlib.Path(get_library_path(catalog_path))
    if not library_dir.exists():
        verrors.add('library', 'Library directory is missing')

    verrors.check()

    hashes = get_hashes_of_base_lib_versions(catalog_path)
    hashes_file_path = get_library_hashes_path(get_library_path(catalog_path))
    with open(hashes_file_path, 'w') as f:
        yaml.safe_dump(hashes, f)

    print(f'[\033[92mOK\x1B[0m]\tGenerated hashes for library versions at {hashes_file_path!r}')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', help='Specify path of TrueNAS catalog')

    args = parser.parse_args()
    if not args.path:
        parser.print_help()
    else:
        update_catalog_hashes(args.path)


if __name__ == '__main__':
    main()

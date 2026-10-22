#!/usr/bin/env python
import argparse

from apps_ci.git import check_no_committed_library_copies, get_changed_apps
from apps_validation.validate_dev_directory import validate_dev_directory_structure
from catalog_reader.library import prepare_dev_apps_libraries


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='sub-command help', dest='action')

    parser_setup = subparsers.add_parser(
        'validate', help='Validate TrueNAS dev catalog items'
    )
    parser_setup.add_argument('--path', help='Specify path of TrueNAS dev catalog', required=True)
    parser_setup.add_argument(
        '--base_branch', help='Specify base branch to find changed catalog items', default='master'
    )

    args = parser.parse_args()
    if args.action == 'validate':
        check_no_committed_library_copies(args.path)
        changed_apps = get_changed_apps(args.path, args.base_branch)
        prepare_dev_apps_libraries(args.path, changed_apps)
        validate_dev_directory_structure(args.path, changed_apps)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()

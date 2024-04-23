#!/usr/bin/env python
import argparse

from apps_validation.ci.git import get_changed_apps
from apps_validation.validation.validate_dev_directory import validate_dev_directory_structure


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
        validate_dev_directory_structure(args.path, get_changed_apps(args.path, args.base_branch))
    else:
        parser.print_help()


if __name__ == '__main__':
    main()

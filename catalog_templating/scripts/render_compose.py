#!/usr/bin/env python
import argparse
import os
import shutil

from apps_validation.exceptions import ValidationErrors
from catalog_reader.app_utils import get_values
from catalog_templating.render import render_templates


def render_templates_from_path(app_path: str, values_file: str) -> None:
    verrors = ValidationErrors()
    for k, v in (('app_path', app_path), ('values_file', values_file)):
        if not os.path.exists(v):
            verrors.add(k, f'{v!r} {k} does not exist')

    verrors.check()

    rendered_data = render_templates(app_path, get_values(values_file))
    write_template_yaml(app_path, rendered_data)


def write_template_yaml(app_path: str, rendered_templates: dict) -> None:
    rendered_templates_path = os.path.join(app_path, 'templates', 'rendered')
    shutil.rmtree(rendered_templates_path, ignore_errors=True)
    os.makedirs(rendered_templates_path)

    for file_name, rendered_template in rendered_templates.items():
        with open(os.path.join(rendered_templates_path, file_name), 'w') as f:
            f.write(rendered_template)


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='sub-command help', dest='action')

    parser_setup = subparsers.add_parser(
        'render', help='Render TrueNAS catalog app\'s docker compose files'
    )
    parser_setup.add_argument('--path', help='Specify path of TrueNAS app version', required=True)
    parser_setup.add_argument('--values', help='Specify values to be used for rendering the app version', required=True)

    args = parser.parse_args()
    if args.action == 'render':
        render_templates_from_path(args.path, args.values)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()

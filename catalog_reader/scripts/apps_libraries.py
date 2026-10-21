#!/usr/bin/env python
import argparse
import os

from apps_exceptions import AppDoesNotExist, CatalogDoesNotExist, ValidationErrors
from catalog_reader.dev_directory import get_ci_development_directory
from catalog_reader.library import copy_app_libraries


def prepare_dev_apps_libraries(catalog_path: str, to_prepare_apps: dict[str, list[str]] | None = None) -> None:
    """
    Copy the libraries into the dev directory apps, all of them or only to_prepare_apps ({train: [app, ...]}),
    so they can be rendered and validated. The copies are not to be committed, publish makes its own
    """
    if not os.path.exists(catalog_path):
        raise CatalogDoesNotExist(catalog_path)

    verrors = ValidationErrors()
    dev_directory = get_ci_development_directory(catalog_path)
    for train_name in sorted(os.listdir(dev_directory)):
        train_path = os.path.join(dev_directory, train_name)
        if not os.path.isdir(train_path) or (to_prepare_apps is not None and train_name not in to_prepare_apps):
            continue

        for app_name in sorted(os.listdir(train_path)):
            app_path = os.path.join(train_path, app_name)
            if to_prepare_apps is not None and app_name not in to_prepare_apps[train_name]:
                continue
            if not os.path.isfile(os.path.join(app_path, 'app.yaml')):
                continue

            try:
                copy_app_libraries(catalog_path, app_path)
            except ValidationErrors as e:
                verrors.add_child(f'dev.{train_name}.{app_name}', e)

    verrors.check()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', help='Specify path of TrueNAS catalog', required=True)
    parser.add_argument('--train', type=str, help='Specify a train name (must be used with --app)')
    parser.add_argument('--app', type=str, help='Specify a single app name to prepare (must be used with --train)')

    args = parser.parse_args()
    if bool(args.train) != bool(args.app):
        parser.error('Both --train and --app must be specified together')
    app_path = os.path.join(get_ci_development_directory(args.path), args.train or '', args.app or '')
    if args.train and not os.path.isdir(app_path):
        raise AppDoesNotExist(app_path)

    prepare_dev_apps_libraries(args.path, {args.train: [args.app]} if args.train else None)
    print('[\033[92mOK\x1B[0m]\tCopied the libraries into the apps')


if __name__ == '__main__':
    main()

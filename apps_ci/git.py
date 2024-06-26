import os
import subprocess
from collections import defaultdict

from apps_exceptions import CatalogDoesNotExist
from catalog_reader.dev_directory import (
    DEV_DIRECTORY_RELATIVE_PATH, get_ci_development_directory, OPTIONAL_METADATA_FILES
)
from catalog_reader.train_utils import is_train_valid


def get_changed_apps(catalog_path: str, base_branch: str = 'master') -> dict:
    if not os.path.exists(catalog_path):
        raise CatalogDoesNotExist(catalog_path)

    cp = subprocess.run(
        ['git', '-C', catalog_path, '--no-pager', 'diff', '--name-only', base_branch],
        capture_output=True, check=True,
    )
    dev_directory_path = get_ci_development_directory(catalog_path)
    to_check_apps = defaultdict(list)
    for file_path in filter(
        lambda path: path and path.startswith(f'{DEV_DIRECTORY_RELATIVE_PATH}/'),
        map(str.strip, cp.stdout.decode().split('\n'))
    ):
        dev_dir_relative_path = file_path.strip(f'{DEV_DIRECTORY_RELATIVE_PATH}/')
        train_name = dev_dir_relative_path.split('/', 1)[0]
        if not is_train_valid(train_name, os.path.join(dev_directory_path, train_name)):
            continue

        app_name = dev_dir_relative_path.split('/')[1]
        base_name = os.path.basename(file_path)

        if base_name in OPTIONAL_METADATA_FILES:
            continue
        if not os.path.isdir(os.path.join(dev_directory_path, train_name, app_name)):
            continue

        if app_name not in to_check_apps[train_name]:
            to_check_apps[train_name].append(app_name)

    return to_check_apps

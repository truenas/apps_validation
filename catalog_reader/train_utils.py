import os

from apps_validation.names import RE_TRAIN_NAME


def is_train_valid(train_name: str, train_location: str) -> bool:
    return RE_TRAIN_NAME.match(train_name) and os.path.isdir(train_location)


def get_train_path(catalog_location: str) -> str:
    return os.path.join(catalog_location, 'trains')

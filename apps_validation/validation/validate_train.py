import os
import typing

from apps_validation.exceptions import ValidationErrors

from .names import RE_TRAIN_NAME


def validate_train_structure(train_path: str, schema: str):
    train = os.path.basename(train_path)
    verrors = ValidationErrors()
    if not RE_TRAIN_NAME.match(train):
        verrors.add(f'{schema}.{train}', 'Train name is invalid')

    verrors.check()


def get_train_items(train_path: str) -> typing.List[typing.Tuple[str, str]]:
    train = os.path.basename(train_path)
    items = []
    for catalog_item in os.listdir(train_path):
        item_path = os.path.join(train_path, catalog_item)
        if not os.path.isdir(item_path):
            continue
        items.append((item_path, f'trains.{train}.{catalog_item}', train))
    return items

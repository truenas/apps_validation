import os
import pathlib
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
    # TODO: do we really need to iterate over every file in `train_paths`??
    # what happens if this directory stores a ton of files? Seems like
    # we could do this differently
    return [
        (
            i.as_posix(),  # full path
            f'trains.{train}.{i.name}',
            train,
        ) for i in filter(lambda x: x.is_dir(), pathlib.Path(train_path).iterdir())
    ]

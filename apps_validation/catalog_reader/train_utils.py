import os

from apps_validation.validation.names import RE_TRAIN_NAME


def get_valid_trains(train_name: str, train_location: str) -> bool:
    return RE_TRAIN_NAME.match(train_name) and os.path.isdir(train_location)

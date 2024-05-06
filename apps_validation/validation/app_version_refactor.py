import os
import yaml

from typing import Optional

from apps_validation.exceptions import ValidationErrors


def validate_app_version_file(
    verrors: ValidationErrors, app_version_path: str, schema: str, item_name: str, version_name: Optional[str] = None,
    train_name: Optional[str] = None,
) -> ValidationErrors:
    if not os.path.exists(app_version_path):
        verrors.add(
            schema, f'App version file {app_version_path!r} does not exist'
        )
        return verrors

    with open(app_version_path, 'r') as f:
        try:
            app_config = yaml.safe_load(f.read())
        except yaml.YAMLError:
            verrors.add(schema, 'Must be a valid yaml file')
            return verrors

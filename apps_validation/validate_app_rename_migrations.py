import json
import jsonschema
import os
import re

from apps_exceptions import ValidationErrors

from .json_schema_utils import APP_MIGRATION_SCHEMA


MIGRATION_NAME_STR = r'^\d+\w+.json'
RE_MIGRATION_NAME = re.compile(MIGRATION_NAME_STR)


def validate_migrations(migration_dir: str):
    verrors = ValidationErrors()
    if not os.path.exists(migration_dir):
        return

    if not os.path.isdir(migration_dir):
        verrors.add('app_migrations', f'{migration_dir!r} must be a directory')
        verrors.check()

    for migration_file in os.listdir(migration_dir):
        if not RE_MIGRATION_NAME.findall(migration_file):
            verrors.add(
                f'app_migrations.{migration_file}',
                'Invalid naming scheme used for migration file name. '
                f'It should be conforming to {MIGRATION_NAME_STR!r} pattern.'
            )
        else:
            try:
                with open(os.path.join(migration_dir, migration_file), 'r') as f:
                    data = json.loads(f.read())
                jsonschema.validate(data, APP_MIGRATION_SCHEMA)
            except (json.JSONDecodeError, jsonschema.ValidationError) as e:
                verrors.add(
                    f'app_migrations.{migration_file}',
                    f'Failed to validate migration file structure: {e}'
                )
    verrors.check()

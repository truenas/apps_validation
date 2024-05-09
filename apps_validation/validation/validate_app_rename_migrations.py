import json
import pathlib

import jsonschema

from apps_validation.exceptions import ValidationErrors

from .json_schema_utils import APP_MIGRATION_SCHEMA


def validate_migrations(migration_dir: str):
    verrors = ValidationErrors()
    suffix = '.json'
    try:
        for migration_file in filter(lambda x: x.is_file(), pathlib.Path(migration_dir).iterdir()):
            schema_str = f'app_migrations.{migration_file.name}'
            if migration_file.suffix != suffix:
                verrors.add(schema_str, f'File suffix must be {suffix}')
            elif not migration_file[0].isdigit():
                verrors.add(schema_str, 'File must start with a digit')
            else:
                jsonschema.validate(json.loads(migration_file.read_text()), APP_MIGRATION_SCHEMA)
    except FileNotFoundError:
        return
    except NotADirectoryError:
        verrors.add('app_migrations', f'{migration_dir!r} must be a directory')
    except (json.JSONDecodeError, jsonschema.ValidationError) as e:
        verrors.add(f'app_migrations.{migration_file}', f'Failed to validate migration file structure: {e}')

    verrors.check()

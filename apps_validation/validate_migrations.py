import os
import yaml

from jsonschema import validate, ValidationError as JsonValidationError

from apps_exceptions import ValidationErrors

from .json_schema_utils import APP_CONFIG_MIGRATIONS_SCHEMA


def get_migration_file_names(migration_yaml_path: str, schema: str) -> list[str]:
    verrors = ValidationErrors()
    try:
        with open(migration_yaml_path, 'r') as f:
            yaml_data = yaml.safe_load(f)
            # Collect file names from the migrations
            files = [migration['file'] for migration in yaml_data['migrations']]
        return files
    except FileNotFoundError:
        return []
    except yaml.YAMLError:
        verrors.add(f'{schema}.yaml_file', 'Must be a valid YAML file')

    verrors.check()


def validate_migration_config(migration_yaml_path: str, schema: str):
    verrors = ValidationErrors()
    with open(migration_yaml_path, 'r') as f:
        try:
            data = yaml.safe_load(f)
        except yaml.YAMLError:
            verrors.add(f'{schema}.yaml_file', 'Must be a valid YAML file')

    verrors.check()

    try:
        validate(instance=data, schema=APP_CONFIG_MIGRATIONS_SCHEMA)
    except JsonValidationError as e:
        verrors.add(f'{schema}', f'Invalid format specified for app migrations: {e.message}')

    verrors.check()


def validate_migration_file(migration_file_path: str, schema: str):
    verrors = ValidationErrors()
    if not os.path.isfile(migration_file_path):
        verrors.add(schema, f"{migration_file_path} is not a valid file")
    else:
        if not os.access(migration_file_path, os.X_OK):
            verrors.add(schema, f"{migration_file_path} is not executable")

        with open(migration_file_path, 'r') as r:
            if not r.readline().startswith('#!'):
                verrors.add(schema, 'Migration file should start with shebang line')

    verrors.check()

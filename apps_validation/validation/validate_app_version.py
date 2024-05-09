import os
import typing
import yaml

from jsonschema import validate as json_schema_validate, ValidationError as JsonValidationError
from semantic_version import Version

from apps_validation.exceptions import ValidationErrors
from catalog_reader.app_utils import get_app_basic_details
from catalog_reader.questions_util import CUSTOM_PORTALS_KEY

from .app_version import validate_app_version_file
from .ix_values import validate_ix_values_schema
from .json_schema_utils import METADATA_JSON_SCHEMA, VERSION_VALIDATION_SCHEMA
from .names import TEST_VALUES_FILENAME
from .validate_questions import validate_questions_yaml
from .validate_templates import validate_templates


def required_files_for_item_version():
    return (
        'app.yaml',
        'questions.yaml',
        'README.md',
        TEST_VALUES_FILENAME,
    )


def validate_catalog_item_version_data(version_data: dict, schema: str, verrors: ValidationErrors) -> ValidationErrors:
    try:
        json_schema_validate(version_data, VERSION_VALIDATION_SCHEMA)
    except JsonValidationError as e:
        verrors.add(schema, f'Invalid format specified for application versions: {e}')
    return verrors


def validate_catalog_item_version(
    version_path: str, schema: str, version_name: typing.Optional[str] = None,
    item_name: typing.Optional[str] = None, validate_values: bool = False, train_name: typing.Optional[str] = None,
):
    verrors = ValidationErrors()
    version_name = version_name or os.path.basename(version_path)
    item_name = item_name or version_path.split('/')[-2]
    try:
        Version(version_name)
    except ValueError:
        verrors.add(f'{schema}.name', f'{version_name!r} is not a valid version name.')

    missing = list()
    for i in required_files_for_item_version():
        _path = os.path_join(version_path, i)
        try:
            if os.path.isdir(_path):
                verrors.add(f'{schema}.required_files', f'{_path!r} must be a file, not a directory')
        except FileNotFoundError:
            missing.append(_path)

    if missing:
        verrors.add(f'{schema}.required_files', f'The following config files are missing: {", ".join(missing)!r}.')

    app_version_path = os.path.join(version_path, 'app.yaml')
    validate_app_version_file(verrors, app_version_path, schema, item_name, version_name, train_name=train_name)
    app_basic_details = get_app_basic_details(version_path)
    if app_basic_details.get('lib_version') is not None:
        # Now we just want to make sure that actual directory for this lib version exists
        version = f'base_v{app_basic_details["lib_version"]}'
        dir_path = f'{version.replace(".", "_")}'
        try:
            is_dir = os.path.isdir(os.path.join(version_path, 'templates/library', dir_path))
            if not is_dir:
                verrors.add(f'{schema}.lib_version', f'{dir_path!r} must be a directory')
        except FileNotFoundError:
            verrors.add(f'{schema}.lib_version', f'{version!r} library version does not exist')

    questions_path = os.path.join(version_path, 'questions.yaml')
    try:
        validate_questions_yaml(questions_path, f'{schema}.questions_configuration')
    except ValidationErrors as v:
        verrors.extend(v)
    except FileNotFoundError:
        verrors.add(f'{schema}.questions_configuration', f'{questions_path!r} not found')

    validate_templates(version_path, f'{schema}.templates')

    # FIXME: values.yaml is probably not needed here
    for values_file in ['ix_values.yaml'] + (['values.yaml'] if validate_values else []):
        values_path = os.path.join(version_path, values_file)
        try:
            validate_ix_values_yaml(values_path, f'{schema}.values_configuration')
        except ValidationErrors as v:
            verrors.extend(v)
        except FileNotFoundError:
            verrors.add(f'{schema}.values_configuration', f'{values_path!r} not found')

    metadata_path = os.path.join(version_path, 'metadata.yaml')
    try:
        validate_metadata_yaml(metadata_path, f'{schema}.metadata_configuration')
    except ValidationErrors as v:
        verrors.extend(v)
    except FileNotFoundError:
        verrors.add(f'{schema}.metadata_configuration', f'{metadata_path!r} not found')

    # validate_app_migrations(verrors, version_path, f'{schema}.app_migrations')
    # FIXME: Add validation for app migrations

    verrors.check()


def validate_ix_values_yaml(ix_values_yaml_path: str, schema: str):
    verrors = ValidationErrors()

    with open(ix_values_yaml_path, 'r') as f:
        try:
            ix_values = yaml.safe_load(f.read())
        except yaml.YAMLError:
            verrors.add(schema, 'Must be a valid yaml file')

        verrors.check()

    if isinstance(ix_values, dict):
        portals = ix_values.get(CUSTOM_PORTALS_KEY)
        if portals:
            try:
                validate_ix_values_schema(schema, portals)
            except ValidationErrors as ve:
                verrors.extend(ve)
    else:
        verrors.add(schema, 'Must be a dictionary')

    verrors.check()


def validate_metadata_yaml(metadata_yaml_path: str, schema: str):
    verrors = ValidationErrors()
    with open(metadata_yaml_path, 'r') as f:
        try:
            metadata = yaml.safe_load(f.read())
            json_schema_validate(metadata, METADATA_JSON_SCHEMA)
        except yaml.YAMLError:
            verrors.add(schema, 'Must be a valid yaml file')
        except JsonValidationError as e:
            verrors.add(schema, f'Invalid format specified for application metadata: {e}')

    verrors.check()

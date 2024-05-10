import os
import pathlib
import typing
import yaml

from jsonschema import validate as json_schema_validate, ValidationError as JsonValidationError
from semantic_version import Version

from apps_validation.exceptions import ValidationErrors
from catalog_reader.app_utils import get_app_basic_details
from catalog_reader.hash_utils import get_hash_of_directory
from catalog_reader.names import get_base_library_dir_name_from_version
from catalog_reader.questions_util import CUSTOM_PORTALS_KEY

from .app_version import validate_app_version_file
from .ix_values import validate_ix_values_schema
from .json_schema_utils import METADATA_JSON_SCHEMA, VERSION_VALIDATION_SCHEMA
from .validate_questions import validate_questions_yaml
from .validate_templates import validate_templates


WANTED_FILES_IN_ITEM_VERSION = {
    'app.yaml',
    'questions.yaml',
    'README.md',
}


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

    files_diff = WANTED_FILES_IN_ITEM_VERSION ^ set(
        f for f in os.listdir(version_path) if f in WANTED_FILES_IN_ITEM_VERSION
    )
    if files_diff:
        verrors.add(f'{schema}.required_files', f'Missing {", ".join(files_diff)} required configuration files.')

    app_version_path = os.path.join(version_path, 'app.yaml')
    validate_app_version_file(verrors, app_version_path, schema, item_name, version_name, train_name=train_name)
    app_basic_details = get_app_basic_details(version_path)
    if app_basic_details.get('lib_version') is not None:
        # Now we just want to make sure that actual directory for this lib version exists
        base_lib_dir = pathlib.Path(os.path.join(
            version_path, 'templates/library',
            get_base_library_dir_name_from_version(app_basic_details['lib_version'])
        ))
        if not base_lib_dir.exists():
            verrors.add(
                f'{schema}.lib_version',
                f'Specified {app_basic_details["lib_version"]!r} library version does not exist'
            )
        elif not base_lib_dir.is_dir():
            verrors.add(f'{schema}.lib_version', f'{base_lib_dir!r} is not a directory')
        elif get_hash_of_directory(str(base_lib_dir)) != app_basic_details['lib_version_hash']:
            verrors.add(f'{schema}.lib_version', 'Library version hash does not match with the actual library version')

    questions_path = os.path.join(version_path, 'questions.yaml')
    if os.path.exists(questions_path):
        try:
            validate_questions_yaml(questions_path, f'{schema}.questions_configuration')
        except ValidationErrors as v:
            verrors.extend(v)

    validate_templates(version_path, f'{schema}.templates', verrors)

    # FIXME: values.yaml is probably not needed here
    for values_file in ['ix_values.yaml'] + (['values.yaml'] if validate_values else []):
        values_path = os.path.join(version_path, values_file)
        if os.path.exists(values_path):
            try:
                validate_ix_values_yaml(values_path, f'{schema}.values_configuration')
            except ValidationErrors as v:
                verrors.extend(v)

    metadata_path = os.path.join(version_path, 'metadata.yaml')
    if os.path.exists(metadata_path):
        try:
            validate_metadata_yaml(metadata_path, f'{schema}.metadata_configuration')
        except ValidationErrors as v:
            verrors.extend(v)

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
        except yaml.YAMLError:
            verrors.add(schema, 'Must be a valid yaml file')
        else:
            try:
                json_schema_validate(metadata, METADATA_JSON_SCHEMA)
            except JsonValidationError as e:
                verrors.add(schema, f'Invalid format specified for application metadata: {e}')

    verrors.check()

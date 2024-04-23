import json
import typing

from jsonschema import validate as json_schema_validate, ValidationError as JsonValidationError

from apps_validation.catalog_reader.catalog import retrieve_train_names, retrieve_trains_data, get_apps_in_trains
from apps_validation.exceptions import ValidationErrors
from apps_validation.validation.json_schema_utils import CATALOG_JSON_SCHEMA
from apps_validation.validation.validate_app_version import validate_catalog_item_version_data


def get_trains(location: str) -> typing.Tuple[dict, dict]:
    preferred_trains: list = []
    trains_to_traverse = retrieve_train_names(location)
    catalog_data = {}
    versions_data = {}
    for train_name, train_data in retrieve_trains_data(
        get_apps_in_trains(trains_to_traverse, location), location, preferred_trains, trains_to_traverse
    )[0].items():
        catalog_data[train_name] = {}
        versions_data[train_name] = {}
        for app_name, app_data in train_data.items():
            catalog_data[train_name][app_name] = {}
            versions_data[train_name][app_name] = {}
            for k, v in app_data.items():
                if k == 'versions':
                    versions_data[train_name][app_name][k] = v
                else:
                    catalog_data[train_name][app_name][k] = v

    return catalog_data, versions_data


def validate_train_data(train_data):
    verrors = ValidationErrors()
    try:
        json_schema_validate(train_data, CATALOG_JSON_SCHEMA)
    except (json.JSONDecodeError, JsonValidationError) as e:
        verrors.add(
            'catalog_json',
            f'Failed to validate contents of train data: {e!r}'
        )
    verrors.check()


def validate_versions_data(versions_data):
    verrors = ValidationErrors()
    for train_name, train_data in versions_data.items():
        for app_name, app_version_data in train_data.items():
            validate_catalog_item_version_data(app_version_data['versions'], f'{train_name}.{app_name}', verrors)
    verrors.check()

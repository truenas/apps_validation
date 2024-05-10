import concurrent.futures
import json
import os

from jsonschema import validate as json_schema_validate, ValidationError as JsonValidationError

from apps_ci.names import CACHED_CATALOG_FILE_NAME
from apps_exceptions import CatalogDoesNotExist, ValidationErrors
from catalog_reader.train_utils import get_train_path

from .json_schema_utils import CATALOG_JSON_SCHEMA
from .validate_app_rename_migrations import validate_migrations
from .validate_app import validate_catalog_item
from .validate_library import validate_base_libraries
from .validate_recommended_apps import validate_recommended_apps_file
from .validate_train import get_train_items, validate_train_structure


def validate_catalog(catalog_path: str):
    if not os.path.exists(catalog_path):
        raise CatalogDoesNotExist(catalog_path)

    verrors = ValidationErrors()
    items = []
    item_futures = []
    cached_catalog_file_path = os.path.join(catalog_path, CACHED_CATALOG_FILE_NAME)
    if not os.path.exists(cached_catalog_file_path):
        verrors.add(
            'cached_catalog_file',
            f'{CACHED_CATALOG_FILE_NAME!r} metadata file must be specified for a valid catalog'
        )
    else:
        try:
            with open(cached_catalog_file_path, 'r') as f:
                json_schema_validate(json.loads(f.read()), CATALOG_JSON_SCHEMA)

        except (json.JSONDecodeError, JsonValidationError) as e:
            verrors.add(
                'cached_catalog_file',
                f'Failed to validate contents of {cached_catalog_file_path!r}: {e!r}'
            )

    verrors.check()

    validate_base_libraries(catalog_path, verrors)

    for method, params in (
        (validate_recommended_apps_file, (catalog_path,)),
        (validate_migrations, (os.path.join(catalog_path, 'migrations'),)),
    ):
        try:
            method(*params)
        except ValidationErrors as e:
            verrors.extend(e)

    trains_dir = get_train_path(catalog_path)
    if not os.path.exists(trains_dir):
        verrors.add('trains', 'Trains directory is missing')
    elif not os.path.isdir(trains_dir):
        verrors.add('trains', f'{trains_dir!r} must be a directory')

    for train_name in os.listdir(trains_dir):
        train_path = os.path.join(trains_dir, train_name)
        if not os.path.isdir(train_path):
            continue
        try:
            validate_train_structure(train_path, 'trains')
        except ValidationErrors as e:
            verrors.extend(e)
        else:
            items.extend(get_train_items(train_path))

    with concurrent.futures.ProcessPoolExecutor(max_workers=5 if len(items) > 10 else 2) as exc:
        for item in items:
            item_futures.append(exc.submit(validate_catalog_item, item[0], item[1], item[2], True))

        for future in item_futures:
            try:
                future.result()
            except ValidationErrors as e:
                verrors.extend(e)

    verrors.check()

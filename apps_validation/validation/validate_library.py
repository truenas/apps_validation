import os.path
import pathlib

from jsonschema import validate as json_schema_validate, ValidationError as JsonValidationError

from apps_validation.exceptions import ValidationErrors
from catalog_reader.library import get_library_hashes, get_hashes_of_base_lib_versions, RE_VERSION
from catalog_reader.names import get_library_path, get_library_hashes_path

from .json_schema_utils import BASE_LIBRARIES_JSON_SCHEMA


def validate_base_libraries(catalog_path: str, verrors: ValidationErrors) -> None:
    library_path = get_library_path(catalog_path)
    library_path_obj = pathlib.Path(library_path)
    if not library_path_obj.exists():
        return

    if any(
        entry for entry in library_path_obj.iterdir() if entry.is_dir() and RE_VERSION.match(entry.name)
    ) and not pathlib.Path(get_library_hashes_path(library_path)).exists():
        verrors.add('library', 'Library hashes file is missing')

    verrors.check()

    get_local_hashes_contents = get_library_hashes(library_path)
    try:
        json_schema_validate(get_local_hashes_contents, BASE_LIBRARIES_JSON_SCHEMA)
    except JsonValidationError as e:
        verrors.add('library', f'Invalid format specified for library hashes: {e}')

    verrors.check()

    try:
        hashes = get_hashes_of_base_lib_versions(catalog_path)
    except Exception as e:
        verrors.add('library', f'Error while generating hashes for library versions: {e}')
    else:
        if hashes != get_local_hashes_contents:
            verrors.add(
                'library',
                'Generated hashes for library versions do not match with the existing '
                'hashes file and need to be updated'
            )

    verrors.check()

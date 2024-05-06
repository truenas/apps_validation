import os
import pathlib
import re

from apps_validation.exceptions import ValidationErrors
from catalog_reader.app_utils import get_app_basic_details, get_values
from catalog_templating.render import render_templates

from .names import TEST_VALUES_FILENAME


RE_APP_VERSION = re.compile(r'^v\d+_\d+_\d+$')
RE_BASE_LIB_VERSION = re.compile(r'^base_v\d+_\d+_\d+$')


def validate_templates(app_path: str, schema: str) -> None:
    verrors = ValidationErrors()
    templates_dir = pathlib.Path(os.path.join(app_path, 'templates'))
    if not templates_dir.exists():
        verrors.add(schema, 'Templates directory does not exist')
    elif not templates_dir.is_dir():
        verrors.add(schema, 'Templates is not a directory')
    else:
        if (library_path := templates_dir / 'library').exists():
            if library_path.exists():
                if not library_path.is_dir():
                    verrors.add(f'{schema}.library', 'Library is not a directory')
                else:
                    validate_library(app_path, f'{schema}.library', verrors)

        found_compose_file = False
        for entry in templates_dir.iterdir():
            if entry.name.endswith('.yaml'):
                if not entry.is_file():
                    verrors.add(schema, f'{entry.name!r} template file is not a file')
                else:
                    found_compose_file = True

        if not found_compose_file:
            verrors.add(schema, 'No template files found in templates directory')

    verrors.check()


def validate_library(app_path: str, schema: str, verrors: ValidationErrors) -> None:
    library_dir = pathlib.Path(os.path.join(app_path, 'templates/library'))
    library_contents = list(library_dir.iterdir())
    if not library_contents:
        return
    elif len(library_contents) > 2:
        verrors.add(schema, 'Library directory should only contain library version from the catalog or the app')

    app_config = get_app_basic_details(app_path)
    app_library = pathlib.Path(os.path.join(
        library_dir.name, app_config['train'], app_config['name'], f'v{app_config["version"].replace(".", "_")}'
    ))
    # We expect 2 paths here, one for the base library and one for the app library
    for entry in library_contents:
        if RE_BASE_LIB_VERSION.findall(entry.name):
            if not entry.is_dir():
                verrors.add(schema, f'Base library {entry.name!r} is not a directory')
        elif entry.name == app_config['train']:
            if app_library.exists() and not app_library.is_dir():
                verrors.add(schema, f'App library {app_library.name!r} is not a directory')
        else:
            verrors.add(schema, f'Unexpected library found: {entry.name!r}')

    if verrors:
        # If we have issues, no point in continuing further
        return

    try:
        rendered = render_templates(app_path, get_values(os.path.join(app_path, TEST_VALUES_FILENAME)))
    except Exception as e:
        verrors.add(schema, f'Failed to render templates: {e}')
    else:
        if not rendered:
            verrors.add(schema, 'No templates were rendered')

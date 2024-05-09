import os
import pathlib
import re
import yaml

from apps_validation.exceptions import ValidationErrors
from catalog_reader.app_utils import get_app_basic_details, get_values
from catalog_templating.render import render_templates

from .names import get_test_values_dir_path, get_test_values_from_test_dir


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
        else:
            validate_template_rendering(app_path, schema, verrors)

    verrors.check()


def validate_template_rendering(app_path: str, schema: str, verrors: ValidationErrors) -> None:
    test_values_files = []
    if not pathlib.Path(get_test_values_dir_path(app_path)).exists():
        verrors.add(
            f'{schema}.test_values', f'Test values directory does not exist at {get_test_values_dir_path(app_path)!r}'
        )

    elif not (test_values_files := get_test_values_from_test_dir(app_path)):
        verrors.add(f'{schema}.test_values', 'No test values files found')

    verrors.check()

    for test_values_file in test_values_files:
        try:
            rendered = render_templates(
                app_path, get_values(os.path.join(get_test_values_dir_path(app_path), test_values_file))
            )
        except Exception as e:
            verrors.add(schema, f'Failed to render templates using {test_values_file!r}: {e}')
        else:
            if not rendered:
                verrors.add(schema, f'No templates were rendered with {test_values_file!r}')
            else:
                for file_name, rendered_template in rendered.items():
                    try:
                        yaml.safe_load(rendered_template)
                    except yaml.YAMLError as e:
                        verrors.add(
                            f'{schema}.{file_name}',
                            f'Failed to verify rendered template is a valid yaml file using {test_values_file!r}: {e}'
                        )


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

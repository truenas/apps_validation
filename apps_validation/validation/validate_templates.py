import os
import pathlib

from apps_validation.exceptions import ValidationErrors


def validate_templates(app_path: str, schema: str) -> None:
    verrors = ValidationErrors()
    templates_dir = pathlib.Path(os.path.join(app_path, 'templates'))
    if not templates_dir.exists():
        verrors.add(schema, 'Templates directory does not exist')
    elif not templates_dir.is_dir():
        verrors.add(schema, 'Templates is not a directory')
    else:
        # TODO: Validate library directory
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

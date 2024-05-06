import os
import yaml
from typing import Optional

from semantic_version import Version

from apps_validation.exceptions import ValidationErrors

from .scale_version import validate_min_max_version_values


def validate_app_version_file(
    verrors: ValidationErrors, app_version_path: str, schema: str, item_name: str, version_name: Optional[str] = None,
    train_name: Optional[str] = None,
) -> ValidationErrors:
    if os.path.exists(app_version_path):
        with open(app_version_path, 'r') as f:
            try:
                app_config = yaml.safe_load(f.read())
            except yaml.YAMLError:
                verrors.add(schema, 'Must be a valid yaml file')
            else:
                if not isinstance(app_config, dict):
                    verrors.add(schema, 'Must be a dictionary')
                else:
                    if app_config.get('name') != item_name:
                        verrors.add(f'{schema}.item_name', 'Item name not correctly set in "app.yaml".')

                    if not isinstance(app_config.get('annotations', {}), dict):
                        verrors.add(f'{schema}.annotations', 'Annotations must be a dictionary')
                    elif app_config.get('annotations'):
                        validate_min_max_version_values(app_config['annotations'], verrors, schema)

                    if not isinstance(app_config.get('sources', []), list):
                        verrors.add(f'{schema}.sources', 'Sources must be a list')
                    else:
                        for index, source in enumerate(app_config.get('sources', [])):
                            if not isinstance(source, str):
                                verrors.add(f'{schema}.sources.{index}', 'Source must be a string')

                    if not isinstance(app_config.get('maintainers', []), list):
                        verrors.add(f'{schema}.maintainers', 'Maintainers must be a list')
                    else:
                        for index, maintainer in enumerate(app_config.get('maintainers', [])):
                            if not isinstance(maintainer, dict):
                                verrors.add(f'{schema}.maintainers.{index}', 'Maintainer must be a dictionary')
                            elif not all(k in maintainer and isinstance(maintainer[k], str) for k in ('name', 'email')):
                                verrors.add(
                                    f'{schema}.maintainers.{index}',
                                    'Maintainer must have name and email attributes defined and be strings.'
                                )

                    app_version = app_config.get('version')
                    if app_version is None:
                        verrors.add(f'{schema}.version', 'Version must be configured in "app.yaml"')
                    else:
                        try:
                            Version(app_version)
                        except ValueError:
                            verrors.add(f'{schema}.version', f'{app_version!r} is not a valid version name')

                    if version_name is not None and app_version != version_name:
                        verrors.add(
                            f'{schema}.version',
                            'Configured version in "app.yaml" does not match version directory name.'
                        )

                    # TODO: Validate lib version please
                    if train_name is not None:
                        if app_config.get('train') != train_name:
                            verrors.add(f'{schema}.train', 'Train name not correctly set in "app.yaml".')

    else:
        verrors.add(schema, 'Missing app version file')

    return verrors

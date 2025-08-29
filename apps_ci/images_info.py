import yaml

from pathlib import Path

from apps_exceptions import AppDoesNotExist, ValidationErrors


"""
ix_values.yaml example:
'image' is the 'main' container

images:
  image:
    repository: some_repo
    tag: some_tag
  db_image:
    repository: some_repo
    tag: some_tag
"""


def is_main_dep(app_dir: Path, dep_name: str, dep_version: str) -> bool:
    if not app_dir.is_dir():
        raise AppDoesNotExist(app_dir)
    if not dep_name:
        return False

    verrors = ValidationErrors()
    ix_values = app_dir / 'ix_values.yaml'
    if not ix_values.is_file():
        verrors.add('image_key', f'Missing ix_values.yaml file for {app_dir.name!r}')
    verrors.check()
    with open(ix_values, 'r') as f:
        ix_values_data = yaml.safe_load(f.read())
        main_image = ix_values_data.get('images', {}).get('image', {})
        repo = main_image.get('repository')
        tag = main_image.get('tag')
        if repo == dep_name and tag == dep_version:
            return True

    return False

import pathlib

import pytest

from apps_exceptions import ValidationErrors
from apps_validation.validate_library import validate_used_library_versions


def write_file(path: pathlib.Path, content: str = '') -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


@pytest.fixture
def catalog(tmp_path):
    write_file(tmp_path / 'library/2.0.0/render.py')
    return tmp_path


def validate(catalog: pathlib.Path) -> list[tuple[str, str]]:
    verrors = ValidationErrors()
    validate_used_library_versions(str(catalog), verrors)
    return [(attribute, message) for attribute, message, _ in verrors]


def test_used_library_versions_exist(catalog):
    write_file(catalog / 'ix-dev/stable/app1/app.yaml', 'lib_version: 2.0.0')
    write_file(catalog / 'ix-dev/stable/app2/app.yaml', 'name: app2')

    assert validate(catalog) == []


def test_used_library_version_missing(catalog):
    write_file(catalog / 'ix-dev/stable/app1/app.yaml', 'lib_version: 1.0.0')
    write_file(catalog / 'ix-dev/community/app2/app.yaml', 'lib_version: 1.0.0')
    write_file(catalog / 'ix-dev/community/app3/app.yaml', 'lib_version: 2.0.0')

    assert validate(catalog) == [
        ('library.1.0.0', 'Library version is used by community/app2, stable/app1 but does not exist'),
    ]


def test_used_library_versions_skip_broken_app_config(catalog):
    write_file(catalog / 'ix-dev/stable/app1/app.yaml', 'lib_version: [')
    write_file(catalog / 'ix-dev/stable/app2/app.yaml', '- lib_version')

    assert validate(catalog) == []

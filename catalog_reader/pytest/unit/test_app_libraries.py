import pathlib

import pytest
import yaml

from apps_exceptions import ValidationErrors
from catalog_reader.library import copy_app_libraries


def write_file(path: pathlib.Path, content: str = '') -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def make_app(catalog: pathlib.Path, name: str = 'test_app', lib_version: str = '2.0.0') -> pathlib.Path:
    app = catalog / 'ix-dev/stable' / name
    write_file(app / 'app.yaml', yaml.safe_dump({
        'name': name, 'train': 'stable', 'version': '1.0.1', 'lib_version': lib_version,
    }))
    return app


def library_files(app: pathlib.Path) -> set[str]:
    library_path = app / 'templates/library'
    return {p.relative_to(library_path).as_posix() for p in library_path.rglob('*') if p.is_file()}


@pytest.fixture
def catalog(tmp_path):
    write_file(tmp_path / 'library/2.0.0/render.py')
    write_file(tmp_path / 'library/2.0.0/tests/test_render.py')
    return tmp_path


def test_copy_app_libraries_in_place(catalog):
    app = make_app(catalog)
    write_file(app / 'lib/config.py')
    write_file(app / 'lib/__pycache__/config.cpython-311.pyc')

    copy_app_libraries(str(catalog), str(app))

    assert library_files(app) == {'base_v2_0_0/render.py', 'stable/test_app/v1_0_1/config.py'}


def test_copy_app_libraries_replaces_old_copies(catalog):
    app = make_app(catalog)
    write_file(app / 'lib/config.py')
    write_file(app / 'templates/library/base_v1_0_0/render.py')
    write_file(app / 'templates/library/base_v2_0_0/stale.py')
    write_file(app / 'templates/library/stable/test_app/v1_0_0/config.py')

    copy_app_libraries(str(catalog), str(app))

    assert library_files(app) == {'base_v2_0_0/render.py', 'stable/test_app/v1_0_1/config.py'}


def test_copy_app_libraries_to_destination(catalog, tmp_path):
    app = make_app(catalog)
    write_file(app / 'lib/config.py')
    destination = tmp_path / 'published'

    copy_app_libraries(str(catalog), str(app), str(destination))

    assert library_files(destination) == {'base_v2_0_0/render.py', 'stable/test_app/v1_0_1/config.py'}
    assert not (app / 'templates/library').exists()


def test_copy_app_libraries_missing_library_version(catalog):
    app = make_app(catalog, lib_version='9.9.9')
    write_file(app / 'templates/library/base_v9_9_9/render.py')

    with pytest.raises(ValidationErrors, match='9.9.9'):
        copy_app_libraries(str(catalog), str(app))

    # A failing app keeps the copies it had
    assert library_files(app) == {'base_v9_9_9/render.py'}

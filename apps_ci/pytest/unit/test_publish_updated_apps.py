import pathlib

import pytest
import yaml

from apps_ci.scripts.catalog_update import publish_updated_apps
from apps_exceptions import ValidationErrors


def write_file(path: pathlib.Path, content: str = '') -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def make_app(catalog: pathlib.Path, version: str = '1.0.1', lib_version: str | None = '2.0.0') -> pathlib.Path:
    app = catalog / 'ix-dev/stable/test_app'
    app_config = {'name': 'test_app', 'train': 'stable', 'version': version}
    if lib_version:
        app_config['lib_version'] = lib_version
    write_file(app / 'app.yaml', yaml.safe_dump(app_config))
    write_file(app / 'item.yaml', yaml.safe_dump({'categories': []}))
    write_file(app / 'templates/docker-compose.yaml')
    return app


def published_files(catalog: pathlib.Path, version: str = '1.0.1') -> set[str]:
    version_path = catalog / 'trains/stable/test_app' / version
    return {p.relative_to(version_path).as_posix() for p in version_path.rglob('*') if p.is_file()}


@pytest.fixture
def catalog(tmp_path):
    # This should appear in the published app
    write_file(tmp_path / 'library/2.0.0/render.py')
    # This should not appear in the published app
    write_file(tmp_path / 'library/2.0.0/tests/test_render.py')
    return tmp_path


def test_publish_builds_base_library_from_catalog_library(catalog):
    app = make_app(catalog)
    write_file(app / 'templates/library/base_v1_0_0/render.py')
    write_file(app / 'templates/library/base_v2_0_0/stale.py')

    publish_updated_apps(str(catalog))

    assert published_files(catalog) == {
        'app.yaml',
        'templates/docker-compose.yaml',
        'templates/library/base_v2_0_0/render.py',
    }
    assert (catalog / 'trains/stable/test_app/item.yaml').is_file()


def test_publish_builds_app_library_from_its_source(catalog):
    app = make_app(catalog)
    write_file(app / 'lib/config.py')
    write_file(app / 'lib/__pycache__/config.cpython-311.pyc')
    write_file(app / 'templates/library/stable/test_app/v1_0_0/stale.py')

    publish_updated_apps(str(catalog))

    assert published_files(catalog) == {
        'app.yaml',
        'templates/docker-compose.yaml',
        'templates/library/base_v2_0_0/render.py',
        'templates/library/stable/test_app/v1_0_1/config.py',
    }


def test_publish_drops_app_library_without_source(catalog):
    app = make_app(catalog)
    write_file(app / 'templates/library/stable/test_app/v1_0_1/config.py')

    publish_updated_apps(str(catalog))

    assert published_files(catalog) == {
        'app.yaml',
        'templates/docker-compose.yaml',
        'templates/library/base_v2_0_0/render.py',
    }


def test_publish_without_lib_version(catalog):
    make_app(catalog, lib_version=None)

    publish_updated_apps(str(catalog))

    assert published_files(catalog) == {'app.yaml', 'templates/docker-compose.yaml'}


def test_publish_fails_on_missing_library_version(catalog):
    make_app(catalog, lib_version='9.9.9')

    with pytest.raises(ValidationErrors, match='9.9.9'):
        publish_updated_apps(str(catalog))


def test_publish_removes_older_versions(catalog):
    make_app(catalog)
    write_file(catalog / 'trains/stable/test_app/1.0.0/app.yaml')

    publish_updated_apps(str(catalog))

    assert sorted(p.name for p in (catalog / 'trains/stable/test_app').iterdir()) == ['1.0.1', 'item.yaml']


def test_publish_without_dev_directory(catalog):
    assert publish_updated_apps(str(catalog)) is None  # type: ignore[func-returns-value]

import pathlib

import pytest
import yaml

from apps_ci.scripts.catalog_update import publish_updated_apps


# What the libraries are built from is covered by catalog_reader/pytest/unit/test_app_libraries.py


def write_file(path: pathlib.Path, content: str = '') -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def make_app(catalog: pathlib.Path, version: str = '1.0.1') -> pathlib.Path:
    app = catalog / 'ix-dev/stable/test_app'
    write_file(app / 'app.yaml', yaml.safe_dump({
        'name': 'test_app', 'train': 'stable', 'version': version, 'lib_version': '2.0.0',
    }))
    write_file(app / 'item.yaml', yaml.safe_dump({'categories': []}))
    write_file(app / 'templates/docker-compose.yaml')
    return app


def published_files(catalog: pathlib.Path, version: str = '1.0.1') -> set[str]:
    version_path = catalog / 'trains/stable/test_app' / version
    return {p.relative_to(version_path).as_posix() for p in version_path.rglob('*') if p.is_file()}


@pytest.fixture
def catalog(tmp_path):
    write_file(tmp_path / 'library/2.0.0/render.py')
    return tmp_path


def test_publish_builds_libraries(catalog):
    app = make_app(catalog)
    write_file(app / 'lib/config.py')
    # Copies lying around in the dev directory are not what gets published
    write_file(app / 'templates/library/base_v1_0_0/render.py')
    write_file(app / 'templates/library/stable/test_app/v1_0_0/config.py')

    publish_updated_apps(str(catalog))

    assert published_files(catalog) == {
        'app.yaml',
        'templates/docker-compose.yaml',
        'templates/library/base_v2_0_0/render.py',
        'templates/library/stable/test_app/v1_0_1/config.py',
    }
    assert (catalog / 'trains/stable/test_app/item.yaml').is_file()


def test_publish_removes_older_versions(catalog):
    make_app(catalog)
    write_file(catalog / 'trains/stable/test_app/1.0.0/app.yaml')

    publish_updated_apps(str(catalog))

    assert sorted(p.name for p in (catalog / 'trains/stable/test_app').iterdir()) == ['1.0.1', 'item.yaml']


def test_publish_without_dev_directory(catalog):
    assert publish_updated_apps(str(catalog)) is None  # type: ignore[func-returns-value]

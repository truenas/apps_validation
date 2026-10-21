import pathlib
import subprocess

import pytest

from apps_ci.git import check_no_committed_library_copies
from apps_exceptions import ValidationErrors


@pytest.fixture
def catalog(tmp_path):
    subprocess.run(['git', 'init', '-q', str(tmp_path)], check=True)
    return tmp_path


def add_file(catalog: pathlib.Path, path: str) -> None:
    file_path = catalog / path
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text('')
    subprocess.run(['git', '-C', str(catalog), 'add', '-f', path], check=True)


def test_no_committed_library_copies(catalog):
    add_file(catalog, 'ix-dev/stable/test_app/lib/config.py')
    add_file(catalog, 'ix-dev/stable/test_app/templates/docker-compose.yaml')
    add_file(catalog, 'library/2.0.0/render.py')

    assert check_no_committed_library_copies(str(catalog)) is None  # type: ignore[func-returns-value]


@pytest.mark.parametrize('path', [
    'ix-dev/stable/test_app/templates/library/base_v2_0_0/render.py',
    'ix-dev/stable/test_app/templates/library/stable/test_app/v1_0_1/config.py',
])
def test_committed_library_copies(catalog, path):
    add_file(catalog, path)

    with pytest.raises(ValidationErrors, match='1 library files are committed'):
        check_no_committed_library_copies(str(catalog))

import pathlib
import textwrap

import pytest

from apps_ci.images_info import is_main_dep
from apps_exceptions import AppDoesNotExist, ValidationErrors


@pytest.mark.parametrize('yaml_data, dep_name, dep_version, is_dir, is_file, should_work', [
    (
        textwrap.dedent(
            '''
            images:
                image:
                    repository: ABC
                    tag: some_tag
                db_image:
                    repository: ABC
                    tag: other_tag
            '''
        ),
        'ABC',
        'some_tag',
        True,
        True,
        True

    ),
    (
        textwrap.dedent(
            '''
            images:
                image:
                    repository: ABC-main
                    tag: some_tag
                db_image:
                    repository: ABC-db
                    tag: some_tag
            '''
        ),
        'ABC-db',
        'some_tag',
        False,
        False,
        False

    ),
    (
        textwrap.dedent(
            '''
            images:
                image:
                    repository: some_repo-main
                    tag: some_tag
                db_image:
                    repository: some_repo-db
                    tag: some_tag
            '''
        ),
        'ABC-db',
        'some_tag',
        True,
        True,
        False

    ),
    (
        textwrap.dedent(
            '''
            images:
                image:
                    repository: ABC
                    tag: some_tag
                db_image:
                    repository: ABC
                    tag: some_tag
            '''
        ),
        'ABC',
        'other_tag',
        True,
        False,
        False

    ),
])
def test_is_main_dep(mocker, yaml_data, dep_name, dep_version, is_dir, is_file, should_work):
    mock_file = mocker.mock_open(read_data=yaml_data)
    mocker.patch('builtins.open', mock_file)
    mocker.patch('pathlib.Path.is_dir', return_value=is_dir)
    mocker.patch('pathlib.Path.is_file', return_value=is_file)
    if should_work:
        result = is_main_dep(pathlib.Path('/valid/path'), dep_name, dep_version)
        assert result is True
    elif dep_name not in yaml_data:
        result = is_main_dep(pathlib.Path('/valid/path'), dep_name, dep_version)
        assert result is False
    else:
        with pytest.raises((AppDoesNotExist, ValidationErrors)):
            is_main_dep(pathlib.Path('/valid/path'), dep_name, dep_version)


@pytest.mark.parametrize('tag, dep_version, expected', [
    ('1.2.3@sha256:abcdef0123', '1.2.3', True),
    ('1.2.3@sha256:abcdef0123', '1.2.4', False),
    ('1.2.3', '1.2.3', True),
])
def test_is_main_dep_with_digest_pin(mocker, tag, dep_version, expected):
    yaml_data = textwrap.dedent(
        f'''
        images:
            image:
                repository: ABC
                tag: "{tag}"
        '''
    )
    mocker.patch('builtins.open', mocker.mock_open(read_data=yaml_data))
    mocker.patch('pathlib.Path.is_dir', return_value=True)
    mocker.patch('pathlib.Path.is_file', return_value=True)
    assert is_main_dep(pathlib.Path('/valid/path'), 'ABC', dep_version) is expected

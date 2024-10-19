import pathlib

import pytest

from apps_ci.version_bump import rename_versioned_dir, bump_version
from apps_exceptions import AppDoesNotExist, ValidationErrors


@pytest.mark.parametrize('version, new_version, train_name, is_dir, should_work', [
    (
        '1.0.0',
        '1.0.1',
        'community',
        [True, False, False],
        True
    ),
    (
        '1.0',
        '1.0.1',
        'community',
        [True, False, False],
        False
    ),
    (
        '1.0.0',
        '1.0.1',
        'community',
        [False, True, True],
        False
    ),
    (
        '1.0.0',
        '1.0.1',
        'stable',
        [True, True, True],
        False
    ),

])
def test_rename_versioned_dir(mocker, version, new_version, train_name, is_dir, should_work):
    mocker.patch('pathlib.Path.is_dir', side_effect=is_dir)
    mocker.patch('pathlib.Path.rename', return_value=None)
    if should_work:
        result = rename_versioned_dir(version, new_version, train_name, pathlib.Path('/valid/path'))
        assert result is None
    else:
        with pytest.raises((AppDoesNotExist, ValidationErrors)):
            rename_versioned_dir(version, new_version, train_name, pathlib.Path('/valid/path'))


@pytest.mark.parametrize('version, bump, expected', [
    (
        '1.0.0',
        'minor',
        '1.1.0'
    ),
    (
        '1.0.0',
        'major',
        '2.0.0'
    ),
    (
        '1.0.0',
        'patch',
        '1.0.1'
    )
])
def test_bump_version(version, bump, expected):
    result = bump_version(version, bump)
    assert result == expected


def test_bump_version_Fail():
    with pytest.raises(ValueError):
        bump_version('1.0', 'minor')

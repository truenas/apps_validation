import pytest

from apps_ci.scripts.bump_version import update_app_version
from apps_exceptions import AppDoesNotExist, ValidationErrors


@pytest.mark.parametrize('path, bump, dep, dep_version, yaml, expected_out', [
    (
        '/valid/path',
        'minor',
        'some_repo',
        '1.0.2',
        '''
        version: 1.0.0
        icon_url: https://www.chia.net/wp-content/uploads/2022/09/chia-logo.svg
        sources:
          - https://hub.docker.com/r/emby/embyserver
        ''',
        '\x1b[92mOK\x1b[0m]\tUpdated app \'path\', '
        'set app_version to \'1.0.2\' and bumped version from '
        '\'1.0.0\' to \'1.1.0\'\n'
    )
])
def test_update_app_version(mocker, capsys, path, bump, dep, dep_version, yaml, expected_out):
    mocker.patch('os.path.exists', return_value=True)
    mocker.patch('pathlib.Path.is_file', return_value=True)
    mock_file = mocker.mock_open(read_data=yaml)
    mocker.patch('builtins.open', mock_file)
    mocker.patch('apps_ci.scripts.bump_version.is_main_dep', return_value=True)
    mocker.patch('apps_ci.scripts.bump_version.rename_versioned_dir', return_value=None)
    update_app_version(path, bump, dep, dep_version)
    assert expected_out in capsys.readouterr().out


@pytest.mark.parametrize('path, bump, dep, dep_version, exists, is_file, yaml', [
    (
        '/valid/path',
        'minor',
        'some_repo',
        '1.0.2',
        False,
        True,
        '''
        version: 1.0.0
        icon_url: https://www.chia.net/wp-content/uploads/2022/09/chia-logo.svg
        sources:
          - https://hub.docker.com/r/emby/embyserver
        '''
    ),
    (
        '/valid/path',
        'minor',
        'some_repo',
        '1.0.2',
        True,
        False,
        '''
        version: 1.0.0
        icon_url: https://www.chia.net/wp-content/uploads/2022/09/chia-logo.svg
        sources:
          - https://hub.docker.com/r/emby/embyserver
        '''
    ),
])
def test_update_app_version_Errors(mocker, path, bump, dep, dep_version, exists, is_file, yaml):
    mocker.patch('os.path.exists', return_value=exists)
    mocker.patch('pathlib.Path.is_file', return_value=is_file)
    mock_file = mocker.mock_open(read_data=yaml)
    mocker.patch('builtins.open', mock_file)
    mocker.patch('apps_ci.scripts.bump_version.is_main_dep', return_value=True)
    mocker.patch('apps_ci.scripts.bump_version.rename_versioned_dir', return_value=None)
    with pytest.raises((AppDoesNotExist, ValidationErrors)):
        update_app_version(path, bump, dep, dep_version)

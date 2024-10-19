import collections

import pytest

from apps_ci.scripts.catalog_update import publish_updated_apps


@pytest.mark.parametrize('version, app_name, isdir, listdir_ver, should_work', [
    (
        '1.0.1',
        'test_app',
        [True, True, True],
        ['1.0.0', '1.0.1'],
        True
    ),
    (
        '1.0.0',
        'test_app',
        [False],
        ['1.0.0'],
        False
    ),
    (
        '1.0.1',
        'test_app',
        [True, True, True],
        ['1.0.0'],
        True
    ),
])
def test_publish_updated_apps(mocker, capsys, version, app_name, isdir, listdir_ver, should_work):
    to_publish_apps = collections.defaultdict(list)
    to_publish_apps[version].append({'name': app_name, 'version': version})
    mocker.patch('os.path.isdir', side_effect=isdir)
    mocker.patch('os.makedirs')
    mocker.patch('os.listdir', return_value=listdir_ver)
    mocker.patch('os.path.exists', side_effect=[False, True])
    mocker.patch('shutil.copy')
    mocker.patch('shutil.copytree')
    mocker.patch('shutil.move')
    mocker.patch('shutil.rmtree')

    mocker.patch('apps_ci.scripts.catalog_update.get_apps_to_publish', return_value=to_publish_apps)
    mocker.patch('apps_ci.scripts.catalog_update.get_to_keep_versions', return_value=[version])

    if should_work:
        publish_updated_apps('/path/to/catalog')
        expected_out = (
            f'\x1b[92mOK\x1b[0m]\tPublished '
            f'\'{app_name}\' having \'{version}\' version '
            f'to \'{version}\' train successfully!'
        )
        assert expected_out in capsys.readouterr().out

    else:
        assert publish_updated_apps('/path/to/catalog') is None

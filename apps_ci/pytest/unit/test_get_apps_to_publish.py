import collections

import pytest

from apps_ci.scripts.catalog_update import get_apps_to_publish


@pytest.mark.parametrize('isdir,', [
    [True, True, True],
    [True, False, False],
    [False, False, False]
])
def test_get_apps_to_publish(mocker, isdir):
    mocker.patch('os.listdir', side_effect=[
        ['community'],
        ['app1', 'app2']
    ])
    mocker.patch('os.path.isdir', side_effect=isdir)
    mocker.patch('apps_ci.scripts.catalog_update.version_has_been_bumped', return_value=True)
    mocker.patch('apps_ci.scripts.catalog_update.get_app_version', return_value='1.0.1')

    result = get_apps_to_publish('/path/to/catalog')
    assert isinstance(result, collections.defaultdict)

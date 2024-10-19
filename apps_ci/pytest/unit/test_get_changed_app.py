import collections
import os

import pytest

from apps_ci.git import get_changed_apps
from apps_exceptions import CatalogDoesNotExist


@pytest.mark.parametrize('path, base_branch, path_exists, is_train_valid, should_work', [
    (
        '/valid/path/to/catalog',
        'master',
        True,
        True,
        True
    ),
    (
        '/valid/path/to/catalog',
        'master',
        True,
        False,
        True
    ),
    (
        '/invalid/path/to/catalog',
        'master',
        False,
        False,
        False
    )
])
def test_get_changed_apps(mocker, path, base_branch, path_exists, is_train_valid, should_work):
    mocker.patch('os.path.exists', return_value=path_exists)
    mock_subprocess_run = mocker.patch('subprocess.run')
    mock_subprocess_run.return_value.stdout = b'''
    ix-dev/community/actual-budget/1.1.9/values.yaml
    ix-dev/community/another-app/1.0.0/metadata.yaml
    ix-dev/community/another-app/1.0.0/upgrade_info.json
    '''
    mock_get_ci_development_directory = mocker.patch('catalog_reader.dev_directory.get_ci_development_directory')
    mock_get_ci_development_directory.return_value = '/mock/ci/development'
    mocker.patch('apps_ci.git.is_train_valid', return_value=is_train_valid)
    if should_work:
        result = get_changed_apps(path, base_branch)

        os.path.exists.assert_called_once_with(path)
        mock_subprocess_run.assert_called_once_with(
            ['git', '-C', path, '--no-pager', 'diff', '--name-only', base_branch],
            capture_output=True, check=True,
        )
        assert isinstance(result, collections.defaultdict)
    else:
        with pytest.raises(CatalogDoesNotExist):
            get_changed_apps(path, base_branch)

import pathlib
import pytest

from apps_exceptions import CatalogDoesNotExist, ValidationErrors
from catalog_reader.scripts.apps_hashes import update_catalog_hashes


@pytest.mark.parametrize('path, dir_exists, lib_exists, is_dir, open_yaml, hash, should_work', [
    (
        '/path/to/catalog',
        True,
        True,
        True,
        '''
        screenshots:
          - 'https://www.chia.net/wp-content/uploads/2022/09/chia-logo.svg'
        tags:
          - finance
        categories:
          - storage
          - crypto
        icon_url: https://www.chia.net/wp-content/uploads/2022/09/chia-logo.svg
        sources:
          - https://hub.docker.com/r/emby/embyserver
        ''',
        {'lib1': 'hash1'},
        True
    ),
    (
        '/path/to/catalog',
        False,
        False,
        True,
        '''
        screenshots:
          - 'https://www.chia.net/wp-content/uploads/2022/09/chia-logo.svg'
        tags:
          - finance
        categories:
          - storage
          - crypto
        icon_url: https://www.chia.net/wp-content/uploads/2022/09/chia-logo.svg
        sources:
          - https://hub.docker.com/r/emby/embyserver
        ''',
        {'lib1': 'hash1'},
        False
    ),
    (
        '/path/to/catalog',
        True,
        False,
        True,
        '''
        screenshots:
          - 'https://www.chia.net/wp-content/uploads/2022/09/chia-logo.svg'
        tags:
          - finance
        categories:
          - storage
          - crypto
        icon_url: https://www.chia.net/wp-content/uploads/2022/09/chia-logo.svg
        sources:
          - https://hub.docker.com/r/emby/embyserver
        ''',
        {'lib1': 'hash1'},
        False
    ),
    (
        '/path/to/catalog',
        True,
        True,
        True,
        '''
        screenshots:
          - 'https://www.chia.net/wp-content/uploads/2022/09/chia-logo.svg'
        tags:
          - finance
        categories:
          - storage
          - crypto
        icon_url: https://www.chia.net/wp-content/uploads/2022/09/chia-logo.svg
        sources:
          - https://hub.docker.com/r/emby/embyserver
        ''',
        None,
        True
    ),
    (
        '/path/to/catalog',
        True,
        True,
        False,
        '''
        screenshots:
          - 'https://www.chia.net/wp-content/uploads/2022/09/chia-logo.svg'
        tags:
          - finance
        categories:
          - storage
          - crypto
        icon_url: https://www.chia.net/wp-content/uploads/2022/09/chia-logo.svg
        sources:
          - https://hub.docker.com/r/emby/embyserver
        ''',
        {'lib1': 'hash1'},
        True
    ),
])
def test_update_catalog_hashes(mocker, path, dir_exists, lib_exists, is_dir, open_yaml, hash, should_work):
    mock_file = mocker.mock_open(read_data=open_yaml)
    mocker.patch('os.path.exists', return_value=dir_exists)
    mocker.patch('pathlib.Path.exists', return_value=lib_exists)
    mocker.patch('pathlib.Path.is_dir', return_value=is_dir)
    mocker.patch(
        'pathlib.Path.iterdir',
        return_value=[
            pathlib.Path('path/to/file1'),
            pathlib.Path('path/to/file2')
        ]
    )
    mocker.patch('catalog_reader.scripts.apps_hashes.get_hashes_of_base_lib_versions', return_value=hash)
    mocker.patch('builtins.open', mock_file)
    if should_work:
        assert update_catalog_hashes(path) is None
    else:
        with pytest.raises((CatalogDoesNotExist, ValidationErrors)):
            update_catalog_hashes(path)

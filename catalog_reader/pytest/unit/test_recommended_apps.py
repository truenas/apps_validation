import pytest

from catalog_reader.recommended_apps import retrieve_recommended_apps


@pytest.mark.parametrize('recommended_apps, data', [
    (
        '''
        plex:
            - emby
            - photoprism
        minio:
            - syncthing
            - qbittorent
        ''',
        {
            'plex': ['emby', 'photoprism'],
            'minio': ['syncthing', 'qbittorent']
        },
    ),
    (
        '''
        plex:
            - [ 1923 ]
            - photoprism
        minio:
            - syncthing
            - qbittorent
        ''',
        {},
    )
])
def test_retrieve_recommended_apps(mocker, recommended_apps, data):
    mock_file = mocker.mock_open(read_data=recommended_apps)
    mocker.patch('builtins.open', mock_file)
    assert retrieve_recommended_apps('') == data

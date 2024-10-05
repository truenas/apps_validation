import pytest

from apps_exceptions import ValidationErrors
from apps_validation.validate_recommended_apps import validate_recommended_apps_file


@pytest.mark.parametrize('recommended_apps, should_work', [
    (
        '''
        plex:
            - emby
            - photoprism
        palworld:
            - terraria
            - minecraft
        ''', True
    ),
    (
        '''
        plex
            - emby
            - photoprism
        minio:
            - syncthing
            - qbittorent
        ''', False
    ),
    (
        '', False
    ),
])
def test_recommended_apps_file(mocker, recommended_apps, should_work):
    mock_file = mocker.mock_open(read_data=recommended_apps)
    mocker.patch('builtins.open', mock_file)

    if should_work:
        assert validate_recommended_apps_file('') is None
    else:
        with pytest.raises(ValidationErrors):
            validate_recommended_apps_file('')

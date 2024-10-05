import pytest

from apps_exceptions import ValidationErrors
from apps_validation.validate_k8s_to_docker_migration import validate_k8s_to_docker_migrations


@pytest.mark.parametrize('script, executable, error', [
    (
        '''#!/bin/sh
        echo "executable script"
        ''',
        True,
        ''
    ),
    (
        '''/bin/sh
        echo "No shebang line"
        ''',
        True,
        '[EINVAL] test_schema: Migration file should start with shebang line'
    ),
    (
        '''#!/bin/sh
        echo "Not executable"
        ''',
        False,
        '[EINVAL] test_schema: Migration file is not executable'
    )
])
def test_k8s_to_docker_migration(mocker, script, executable, error):
    mock_file = mocker.mock_open(read_data=script)
    mocker.patch('builtins.open', mock_file)
    mocker.patch('os.access', return_value=executable)
    verrors = ValidationErrors()

    validate_k8s_to_docker_migrations(verrors, '', 'test_schema')
    assert str(verrors).strip() == error

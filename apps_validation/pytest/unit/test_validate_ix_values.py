import pytest

from apps_exceptions import ValidationErrors
from apps_validation.validate_app_version import validate_ix_values_yaml


@pytest.mark.parametrize('schema, test_yaml, should_work', [
    (
        'charts.chia.versions.1.3.38.ix_values',
        '''
        image:
          pull_policy: IfNotPresent
          repository: ixsystems/chia-docker
          tag: v1.6.2
        update_strategy: Recreate
        ix_portals: [{portalName: 'web portal', protocol: 'http', useNodeIP: false, host: '192.168.0.18', port: 9898}]
        ''',
        True
    ),
    (
        'charts.chia.versions.1.3.38.ix_values',
        '''
        image:
          pull_policy: IfNotPresent
          repository: ixsystems/chia-docker
          tag: v1.6.2
        update_strategy: Recreate
        ix_portals: [{portalName: 'web portal', protocol: 'http', useNodeIP: true, port: 9898}]
        ''',
        True
    ),
    (
        'charts.chia.versions.1.3.38.ix_values',
        '''
        image
          pull_policy: IfNotPresent
          repository: ixsystems/chia-docker
          tag v1.6.2
        update_strategy: Recreate
        ix_portals: [{portalName: 'web portal', protocol: 'http', useNodeIP: true, port: 9898}]
        ''',
        False
    ),
    (
        'charts.chia.versions.1.3.38.ix_values',
        '',
        False
    ),
    (
        'charts.chia.versions.1.3.38.ix_values',
        '''
        image:
          pull_policy: IfNotPresent
          repository: ixsystems/chia-docker
          tag: v1.6.2
        update_strategy: Recreate
        ix_portals: [{portalName: 'web portal', port: '9898'}]
        ''',
        False
    ),
])
def test_validate_ix_values_yaml(mocker, schema, test_yaml, should_work):
    mock_file = mocker.mock_open(read_data=test_yaml)
    mocker.patch('builtins.open', mock_file)

    if should_work:
        assert validate_ix_values_yaml('', schema) is None
    else:
        with pytest.raises(ValidationErrors):
            validate_ix_values_yaml('', schema)

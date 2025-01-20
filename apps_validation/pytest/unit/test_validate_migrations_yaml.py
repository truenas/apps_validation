import pytest

from apps_exceptions import ValidationErrors
from apps_validation.validate_migrations import validate_migration_config


@pytest.mark.parametrize('yaml_data, should_work', [
    (
        '''
        migrations:
        - file: always.py
          # Should run for any current/target combination
        - file: only_min_version_from.py
          from:
            min_version: 1.0.0
        ''',
        True
    ),
    (
        '''
        migrations:
        - file: always.py
          # Should run for any current/target combination
        - file: only_min_version_from.py
          target:
            min_version: 1.0.0
            max_version: 2.0.0
        ''',
        True
    ),
    (
        '''
        migrations:
        - file: always.py
          # Should run for any current/target combination
        - file: only_min_version_from.py
          from:
            min_version: 1.0.0
        ''',
        True
    ),
    (
        '''
        migrations:
        - file: always.py
          # Should run for any current/target combination
        ''',
        True
    ),
    (
        '''
        migrations
        - file: always.py
          # Should run for any current/target combination
        - file: only_min_version_from.py
          from:
            min_version: 1.0.0
        ''',
        False
    ),
    (
        '''
        migrations:
        ''',
        False
    ),
    (
        '''
        ''',
        False
    ),
    (
        '''
        migrations
        - file: only_min_version_from.py
          from:
        ''',
        False
    ),
])
def test_validate_migrations_yaml(mocker, yaml_data, should_work):
    mock_file = mocker.mock_open(read_data=yaml_data)
    mocker.patch('builtins.open', mock_file)
    if should_work:
        assert validate_migration_config('/path/to/app_migrations.yaml', 'app_migration_config') is None
    else:
        with pytest.raises(ValidationErrors):
            validate_migration_config('/path/to/app_migrations.yaml', 'app_migration_config')

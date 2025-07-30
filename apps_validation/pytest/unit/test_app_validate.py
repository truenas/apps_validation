import pytest

from apps_exceptions import ValidationErrors
from apps_validation.validate_app_version import WANTED_FILES_IN_ITEM_VERSION, validate_catalog_item_version
from apps_validation.validate_app import validate_catalog_item
from apps_validation.validate_migrations import validate_migration_config
from apps_validation.validate_questions import validate_questions_yaml, validate_variable_uniqueness
from apps_validation.validate_train import validate_train_structure


@pytest.mark.parametrize('train_path, should_work', [
    (
        '/mnt/mypool/ix-applications/catalogs/github_com_truenas_charts_git_master/charts',
        True
    ),
    (
        '/mnt/mypool/ix-applications/catalogs/github com truenas charts git master/charts$',
        False
    )
])
def test_validate_train_path(train_path, should_work):
    if should_work:
        assert validate_train_structure(train_path, 'test_schema') is None
    else:
        with pytest.raises(ValidationErrors):
            validate_train_structure(train_path, 'test_schema')


@pytest.mark.parametrize('test_yaml, should_work', [
    (
        '''
        groups:
          - name: "Machinaris Configuration"
            description: "Configure timezone for machinaris"

        portals:
          web_portal:
            protocols:
              - "http"
            host:
              - "$node_ip"
            ports:
              - "$variable-machinaris_ui_port"

        questions:
          - variable: timezone
            label: "Configure timezone"
            group: "Machinaris Configuration"
            description: "Configure timezone for machinaris"
        ''',
        True
    ),
    (
        '''
        groups
          - name: "Machinaris Configuration"
            description: "Configure timezone for machinaris"

        portals
          web_portal:
            protocols:
              - "http"
            host:
              - "$node_ip"
            ports:
              - "$variable-machinaris_ui_port"

        questions:
          - variable: timezone
            label: "Configure timezone"
            group: "Machinaris Configuration"
            description: "Configure timezone for machinaris"
        ''',
        False
    ),
    (
        '''
        groups:
          - name: "Machinaris Configuration"
            description: "Configure timezone for machinaris"

        portals:
          web_portal:
            - protocols:
            - host:
            - ports:

        questions:
          - variable: timezone
            label: "Configure timezone"
            group: "Machinaris Configuration"
            description: "Configure timezone for machinaris"
        ''',
        False
    ),
    (
        '''
        groups:
          - name: "Machinaris Configuration"
            description: "Configure timezone for machinaris"

        portals:
          123:
            - protocols:
            - host:
            - ports:

        questions:
          - variable: timezone
            label: "Configure timezone"
            group: "Machinaris Configuration"
            description: "Configure timezone for machinaris"
        ''',
        False
    ),
    (
        '''
        groups:
          - name

        portals:
          web_portal:
            protocols:
              - "http"
            host:
              - "$node_ip"
            ports:
              - "$variable-machinaris_ui_port"

        questions:
          - variable: timezone
            label: "Configure timezone"
            group: "Machinaris Configuration"
            description: "Configure timezone for machinaris"
        ''',
        False
    ),
    (
        '''
        - groups: ""
        - portals: ""
        - questions: ""
        ''',
        False
    ),
    (
        '''
        groups:
          - name: "Machinaris Configuration"
            description: "Configure timezone for machinaris"

        portals:
          web_portal:
            protocols:
              - "http"
            host:
              - "$node_ip"
            ports:
              - "$variable-machinaris_ui_port"

        questions:
          - variable: timezone
            label: "Configure timezone"
            group: "Invalid group"
            description: "Configure timezone for machinaris"
        ''',
        False
    ),
    (
        '''
        enableIXPortals: true
        groups:
          - name: "Machinaris Configuration"
            description: "Configure timezone for machinaris"

        questions:
          - variable: timezone
            label: "Configure timezone"
            group: "Invalid group"
            description: "Configure timezone for machinaris"
        ''',
        False
    ),
    (
        '''
        enableIXPortals: true
        iXPortalsGroupName: 'Plex Configuration'
        groups:
          - name: "Machinaris Configuration"
            description: "Configure timezone for machinaris"

        questions:
          - variable: timezone
            label: "Configure timezone"
            group: "Invalid group"
            description: "Configure timezone for machinaris"
        ''',
        False
    ),
    (
        '''
        groups:
          - name: "Machinaris Configuration"
            description: "Configure timezone for machinaris"

        questions:
          - variable: timezone
            label: "Configure timezone"
            group: "Machinaris Configuration"
            description: "Configure timezone for machinaris"
          - variable: timezone
        ''',
        False
    ),
    (
        '''
        groups:
          - name: "Machinaris Configuration"
            description: "Configure timezone for machinaris"

        questions:
          - variable: timezone
            label: "Configure timezone"
            group: "Machinaris Configuration"
            description: "Configure timezone for machinaris"
            subquestions:
              - variable: sub_question
              - variable: sub_question
        ''',
        False
    ),
    (
        '''
        enableIXPortals: true
        iXPortalsGroupName: 'Machinaris Configuration'
        groups:
          - name: "Machinaris Configuration"
            description: "Configure timezone for machinaris"

        questions:
          - variable: timezone
            label: "Configure timezone"
            group: "Machinaris Configuration"
            description: "Configure timezone for machinaris"
        ''',
        True
    )
])
def test_validate_question_yaml(mocker, test_yaml, should_work):
    mock_file = mocker.mock_open(read_data=test_yaml)
    mocker.patch('builtins.open', mock_file)
    mocker.patch('apps_validation.validate_questions.validate_question', return_value=None)

    if should_work:
        assert validate_questions_yaml(test_yaml, 'test_schema') is None
    else:
        with pytest.raises(ValidationErrors):
            validate_questions_yaml(test_yaml, 'test_schema')


@pytest.mark.parametrize('catalog_path, test_yaml, train, item_yaml, should_work', [
    (
        '/mnt/mypool/ix-applications/catalogs/github_com_truenas_charts_git_master/charts/machinaris',
        '''
         categories:
           - storage
           - crypto
         icon_url: https://raw.githubusercontent.com/guydavis/machinaris/main/web/static/machinaris.png
        ''',
        'charts',
        'item.yaml',
        True
    ),
    (
        '/mnt/mypool/ix-applications/catalogs/github_com_truenas_charts_git_master/charts/machinaris',
        '''
         categories:
           - storage
           - crypto
         icon_url: https://raw.githubusercontent.com/guydavis/machinaris/main/web/static/machinaris.png
        ''',
        'charts',
        '',
        False
    ),
    (
        '/mnt/mypool/ix-applications/catalogs/github_com_truenas_charts_git_master/charts/machinaris',
        '''
         - icon_url: https://raw.githubusercontent.com/guydavis/machinaris/main/web/static/machinaris.png
        ''',
        'charts',
        'item.yaml',
        False
    ),
])
def test_validate_catalog_item(mocker, catalog_path, test_yaml, train, item_yaml, should_work):
    mocker.patch('os.path.isdir', side_effect=[True, True, False])
    mocker.patch('os.listdir', return_value=['1.1.13', item_yaml])
    mocker.patch('apps_validation.validate_app.validate_catalog_item_version', return_value=None)
    mock_file = mocker.mock_open(read_data=test_yaml)
    mocker.patch('builtins.open', mock_file)

    if should_work:
        assert validate_catalog_item(catalog_path, 'test_schema', train) is None
    else:
        with pytest.raises(ValidationErrors):
            validate_catalog_item(catalog_path, 'test_schema', train)


@pytest.mark.parametrize('version_path, app_yaml, schema, required_files, should_work', [
    (
        '/mnt/mypool/ix-applications/catalogs/github_com_truenas_charts_git_master/charts/storj/1.0.4',
        '''
        name: storj
        version: 1.0.4
        train: stable
        date_added: '2025-04-08'
        app_version: 1.0.0.8395
        title: storj
        description: Test description
        home: https://storj.com
        sources: [https://storj.com]
        maintainers:
        - email: dev@ixsystems.com
          name: truenas
          url: https://www.truenas.com/
        run_as_context: []
        capabilities: []
        host_mounts: []
        ''',
        'charts.storj.versions.1.0.4',
        WANTED_FILES_IN_ITEM_VERSION,
        True
    ),
    (
        '/mnt/mypool/ix-applications/catalogs/github_com_truenas_charts_git_master/charts/storj/latest',
        '''
        name: storj
        version: 1.0.4
        train: stable
        date_added: '2025-04-08'
        app_version: 1.0.0.8395
        title: storj
        description: Test description
        home: https://storj.com
        sources: [https://storj.com]
        maintainers:
        - email: dev@ixsystems.com
          name: truenas
          url: https://www.truenas.com/
        run_as_context: []
        capabilities: []
        host_mounts: []
        ''',
        'charts.storj.versions.1.0.4',
        WANTED_FILES_IN_ITEM_VERSION,
        False
    ),
    (
        '/mnt/mypool/ix-applications/catalogs/github_com_truenas_charts_git_master/charts/storj/1.0.4',
        '''
        name: storj
        version: 1.0.4
        train: stable
        date_added: '2025-04-08'
        app_version: 1.0.0.8395
        title: storj
        description: Test description
        home: https://storj.com
        sources: [https://storj.com]
        maintainers:
        - email: dev@ixsystems.com
          name: truenas
          url: https://www.truenas.com/
        run_as_context: []
        capabilities: []
        host_mounts: []
        ''',
        'charts.storj.versions.1.0.4',
        'app.yaml',
        False
    ),
])
def test_validate_catalog_item_version(mocker, version_path, app_yaml, schema, required_files, should_work):
    mock_file = mocker.mock_open(read_data=app_yaml)
    mocker.patch('builtins.open', mock_file)
    mocker.patch('os.listdir', return_value=required_files)
    mocker.patch('os.path.exists', return_value=True)
    mocker.patch('apps_validation.validate_app_version.validate_questions_yaml', return_value=None)
    mocker.patch('apps_validation.validate_app_version.validate_ix_values_yaml', return_value=None)
    mocker.patch('apps_validation.validate_app_version.validate_templates', return_value=None)
    mocker.patch('apps_validation.validate_app_version.validate_migration_config', return_value=None)

    if should_work:
        assert validate_catalog_item_version(version_path, schema) is None
    else:
        with pytest.raises(ValidationErrors):
            validate_catalog_item_version(version_path, schema)


@pytest.mark.parametrize('data, schema, should_work', [
    (
        [
            {
                'variable': 'enablePlexPass',
                'label': 'Use PlexPass',
                'group': 'Plex Configuration',
                'schema': {
                    'type': 'boolean',
                    'default': False
                }
            },
            {
                'variable': 'dnsConfig',
                'label': 'DNS Configuration',
                'group': 'Advanced DNS Settings',
                'schema': {
                    'type': 'dict',
                    'attrs': []
                }
            },
        ],
        'plex.questions',
        True
    ),
    (
        [
            {
                'variable': 'enablePlexPass',
                'label': 'Use PlexPass',
                'group': 'Plex Configuration',
                'schema': {
                    'type': 'boolean',
                    'default': False
                }
            },
            {
                'variable': 'enablePlexPass',
                'label': 'DNS Configuration',
                'group': 'Advanced DNS Settings',
                'schema': {
                    'type': 'dict',
                    'attrs': []
                }
            },
        ],
        'plex.questions',
        False
    )
])
def test_validate_variable_uniqueness(data, schema, should_work):
    verrors = ValidationErrors()
    if should_work:
        assert validate_variable_uniqueness(data, schema, verrors) is None
    else:
        with pytest.raises(ValidationErrors):
            validate_variable_uniqueness(data, schema, verrors)


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

import pytest

from apps_ci.scripts.catalog_update import get_trains, update_catalog_file
from apps_exceptions import ValidationErrors


@pytest.fixture
def mock_atomic_write(mocker):
    return mocker.patch('apps_ci.scripts.catalog_update.atomic_write', mocker.mock_open())


@pytest.mark.parametrize('catalog_data, version_data, expected', [
    (
        {
            'community': {
                'actual_budget': {
                    'name': 'Actual Budget',
                    'categories': ['finance', 'budgeting'],
                    'app_readme': 'https://example.com/actual-budget/readme',
                    'location': '/path/to/actual_budget',
                    'healthy': True,
                    'healthy_error': None,
                    'last_update': '2024-10-01 14:30:00',
                    'date_added': '2025-04-08',
                    'recommended': [],
                    'latest_version': '1.2.0',
                    'latest_app_version': '1.2.0',
                    'latest_human_version': 'One point two',
                    'description': 'A budget management application.',
                    'title': 'Actual Budget App',
                    'icon_url': 'https://example.com/actual-budget/icon.png',
                    'maintainers': [
                        {
                            'name': 'Alice Smith',
                            'url': 'https://example.com/alice',
                            'email': 'alice@example.com'
                        },
                    ],
                    'home': 'https://example.com/actual-budget',
                    'tags': ['budget', 'finance', 'money'],
                    'screenshots': [
                        'https://example.com/actual-budget/screenshot1.png',
                    ],
                    'sources': [
                        'https://github.com/example/actual-budget',
                    ]
                },
            }
        },
        {
            'community': {
                'actual_budget': {
                    'versions': {
                        '1.0.1': {
                            'name': 'chia',
                            'categories': [],
                            'app_readme': None,
                            'location': '/mnt/mypool/ix-applications/catalogs/'
                                        'github_com_truenas_charts_git_master/charts/chia',
                            'healthy': True,
                            'healthy_error': None,
                            'supported': True,
                            'required_features': [],
                            'version': '1.0.1',
                            'human_version': '1.15.12',
                            'home': None,
                            'readme': None,
                            'changelog': None,
                            'last_update': '1200-20-00 00:00:00',
                            'date_added': '2025-04-08',
                            'maintainers': {},
                            'app_metadata': {
                                'name': 'chia',
                                'train': 'stable',
                                'version': '1.0.1',
                                'app_version': '1.0.1',
                                'date_added': '2025-04-08',
                                'title': 'chia',
                                'description': 'desc',
                                'home': 'None',
                                'sources': [],
                                'maintainers': [],
                                'run_as_context': [],
                                'capabilities': [],
                                'host_mounts': []
                            },
                            'schema': {
                                'groups': [],
                                'questions': []
                            }
                        }
                    }
                }
            }
        },
        [
            '\x1b[92mOK\x1b[0m]\tUpdated \'/valid/path/catalog.json\' successfully!\n[\x1b[92mOK\x1b[0m]',
            'Updated \'/valid/path/trains/community/actual_budget/app_versions.json'
        ]
    ),
    (
        {
            'community': {
                'actual_budget': {
                    'name': 'Actual Budget',
                    'categories': ['finance', 'budgeting'],
                    'app_readme': 'https://example.com/actual-budget/readme',
                    'location': '/path/to/actual_budget',
                    'healthy': True,
                    'healthy_error': None,
                    'last_update': '2024-10-01 14:30:00',
                    'date_added': '2025-04-08',
                    'recommended': [],
                },
            }
        },
        {
            'community': {
                'actual_budget': {
                    'versions': {
                        '1.0.1': {
                            'name': 'chia',
                            'categories': [],
                            }
                        }
                    }
                }
        },
        'Error'
    )
])
def test_update_catalog_file(mocker, capsys, mock_atomic_write, catalog_data, version_data, expected):
    mocker.patch('apps_ci.scripts.catalog_update.get_trains', return_value=[catalog_data, version_data])
    if expected != 'Error':
        update_catalog_file('/valid/path/')
        stdout = capsys.readouterr()
        for expected_out in expected:
            assert expected_out in stdout.out
    else:
        with pytest.raises(ValidationErrors):
            update_catalog_file('/valid/path/')


RISKS = [{'key': 'host_network', 'label': 'Host Networking'}]
CAPABILITIES = [{'name': 'SYS_ADMIN', 'description': 'test is able to perform system administration operations'}]


@pytest.mark.parametrize('app_metadata, expected', [
    (
        {'capabilities': CAPABILITIES, 'run_as_context': [], 'risks': RISKS},
        {'capabilities': CAPABILITIES, 'run_as_context': [], 'risks': RISKS},
    ),
    # Apps on older libraries have no risks
    (
        {'capabilities': CAPABILITIES, 'run_as_context': []},
        {'capabilities': CAPABILITIES, 'run_as_context': [], 'risks': []},
    ),
])
def test_get_trains_copies_latest_version_metadata(mocker, app_metadata, expected):
    train_data = {
        'community': {
            'test': {
                'name': 'test',
                'latest_version': '1.0.1',
                'versions': {
                    '1.0.0': {'app_metadata': {'capabilities': [], 'run_as_context': [], 'risks': []}},
                    '1.0.1': {'app_metadata': app_metadata},
                },
            },
        },
    }
    mocker.patch('apps_ci.scripts.catalog_update.get_train_path', return_value='/valid/path/trains')
    mocker.patch('apps_ci.scripts.catalog_update.retrieve_train_names', return_value=['community'])
    mocker.patch('apps_ci.scripts.catalog_update.get_apps_in_trains', return_value={})
    mocker.patch('apps_ci.scripts.catalog_update.retrieve_trains_data', return_value=(train_data, set()))

    catalog_data, versions_data = get_trains('/valid/path/')
    assert catalog_data['community']['test'] == {'name': 'test', 'latest_version': '1.0.1', **expected}
    assert list(versions_data['community']['test']['versions']) == ['1.0.0', '1.0.1']

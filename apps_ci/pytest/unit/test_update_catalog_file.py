import pytest

from apps_ci.scripts.catalog_update import update_catalog_file
from apps_exceptions import ValidationErrors


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
                            'maintainers': {},
                            'app_metadata': {
                                'name': 'chia',
                                'train': 'stable',
                                'version': '1.0.1',
                                'app_version': '1.0.1',
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
def test_update_catalog_file(mocker, capsys, catalog_data, version_data, expected):
    mocker.patch('apps_ci.scripts.catalog_update.get_trains', return_value=[catalog_data, version_data])
    mock_file = mocker.mock_open(read_data='')
    mocker.patch('builtins.open', mock_file)
    if expected != 'Error':
        update_catalog_file('/valid/path/')
        stdout = capsys.readouterr()
        for expected_out in expected:
            assert expected_out in stdout.out
    else:
        with pytest.raises(ValidationErrors):
            update_catalog_file('/valid/path/')

import pytest

from catalog_reader.app import get_app_details, get_app_details_impl


QUESTION_CONTEXT = {
    'nic_choices': [],
    'gpus': {},
    'timezones': {'Asia/Saigon': 'Asia/Saigon', 'Asia/Damascus': 'Asia/Damascus'},
    'node_ip': '192.168.0.10',
    'certificates': [],
    'certificate_authorities': [],
    'system.general.config': {'timezone': 'America/Los_Angeles'},
    'schema': {'questions': []}
}


@pytest.mark.parametrize('item_path, options, items_data', [
    (
        '/mnt/mypool/ix-applications/catalogs/github_com_truenas_charts_git_master/charts/chia',
        {'retrieve_versions': True},
        {
            'name': 'chia',
            'categories': [],
            'app_readme': None,
            'location': '/mnt/mypool/ix-applications/catalogs/github_com_truenas_charts_git_master/charts/chia',
            'healthy': True,
            'healthy_error': None,
            'home': None,
            'last_update': None,
            'maintainers': [],
            'latest_version': '1.0.0',
            'latest_app_version': '1.0.0',
            'latest_human_version': '1.0.0',
            'recommended': False,
            'title': 'Chia',
            'description': None,
            'tags': [],
            'screenshots': [],
            'sources': [],
            'versions': {
                '1.0.0': {
                    'healthy': True,
                    'app_metadata': {
                        'app_version': '1.0.0',
                        'maintainers': [],
                        'description': None,
                        'home': None,
                        'sources': []
                    },
                    'readme': None,
                }
            }
        }
    ),
    (
        '/mnt/mypool/ix-applications/catalogs/github_com_truenas_charts_git_master/charts/chia',
        {'retrieve_versions': False},
        {
            'name': 'chia',
            'categories': [],
            'app_readme': None,
            'location': '/mnt/mypool/ix-applications/catalogs/github_com_truenas_charts_git_master/charts/chia',
            'healthy': True,
            'healthy_error': None,
            'home': None,
            'last_update': None,
            'maintainers': [],
            'latest_version': '1.0.0',
            'latest_app_version': '1.0.0',
            'latest_human_version': '1.0.0',
            'recommended': False,
            'title': 'Chia',
            'description': None,
            'tags': [],
            'screenshots': [],
            'sources': [],
        }
    )
])
def test_get_app_details(mocker, item_path, options, items_data):
    mocker.patch('catalog_reader.app.validate_catalog_item', return_value=None)
    mocker.patch('catalog_reader.app.get_app_details_impl', return_value={
        'versions': {
                '1.0.0': {
                    'healthy': True,
                    'app_metadata': {
                        'app_version': '1.0.0',
                        'maintainers': [],
                        'description': None,
                        'home': None,
                        'sources': []
                    },
                    'readme': None,
                }
        }
    })
    assert get_app_details(item_path, QUESTION_CONTEXT, options) == items_data


@pytest.mark.parametrize('item_path,schema,options,expected_data,open_yaml', [
    (
        '/mnt/mypool/ix-applications/catalogs/github_com_truenas_charts_git_master/charts/chia',
        'charts.chia',
        {'retrieve_latest_version': True},
        {
            'categories': ['storage', 'crypto'],
            'icon_url': 'https://www.chia.net/wp-content/uploads/2022/09/chia-logo.svg',
            'screenshots': ['https://www.chia.net/wp-content/uploads/2022/09/chia-logo.svg'],
            'tags': ['finance'],
            'versions': {
                '1.3.37': {
                    'healthy': True,
                    'supported': True,
                    'healthy_error': None,
                    'location': '/mnt/mypool/ix-applications/catalogs/'
                                'github_com_truenas_charts_git_master/charts/chia/1.3.37',
                    'last_update': None,
                    'required_features': [],
                    'human_version': '1.3.37',
                    'version': '1.3.37',
                    'app_metadata': None,
                    'schema': None,
                    'readme': None,
                    'changelog': None
                }
            },
            'sources': ['https://hub.docker.com/r/emby/embyserver']
        },
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
        '''
    ),
])
def test_get_item_details_impl(
    mocker, item_path, schema, options, expected_data, open_yaml,
):
    open_file_data = mocker.mock_open(read_data=open_yaml)
    mocker.patch('builtins.open', open_file_data)
    mocker.patch('os.path.isdir', return_value=True)
    mocker.patch('os.listdir', return_value=['1.3.37'])
    mocker.patch('catalog_reader.app.validate_catalog_item_version', return_value=None)
    mocker.patch('catalog_reader.app.validate_catalog_item', return_value={})
    assert get_app_details_impl(item_path, schema, QUESTION_CONTEXT, options) == expected_data

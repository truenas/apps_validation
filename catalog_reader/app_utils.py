import contextlib
import os
import yaml


def get_app_details_base(retrieve_complete_item_keys: bool = True) -> dict:
    return {
        'app_readme': None,
        'categories': [],
        'description': None,
        'healthy': False,  # healthy means that each version the item hosts is valid and healthy
        'healthy_error': None,  # An error string explaining why the item is not healthy
        'home': None,
        'location': None,
        'latest_version': None,
        'latest_app_version': None,
        'latest_human_version': None,
        'last_update': None,
        'name': None,
        'recommended': False,
        'title': None,
        'maintainers': [],
        'tags': [],
        'screenshots': [],
        'sources': [],
        **({
            'versions': {},
        } if retrieve_complete_item_keys else {}),
    }


def get_default_questions_context() -> dict:
    return {
        'nic_choices': [],
        'gpus': {},
        'timezones': {'Asia/Saigon': 'Asia/Saigon', 'Asia/Damascus': 'Asia/Damascus'},
        'node_ip': '192.168.0.10',
        'certificates': [],
        'certificate_authorities': [],
        'system.general.config': {'timezone': 'America/Los_Angeles'},
        'unused_ports': [i for i in range(1025, 65535)],
    }


def get_app_basic_details(app_path: str) -> dict:
    # This just retrieves app name and app version from app path
    with contextlib.suppress(FileNotFoundError, yaml.YAMLError, KeyError):
        with open(os.path.join(app_path, 'app.yaml'), 'r') as f:
            app_config = yaml.safe_load(f.read())
        return {k: app_config[k] for k in ('name', 'train', 'version', 'lib_version')}

    return {}


def get_values(values_path: str) -> dict:
    with contextlib.suppress(FileNotFoundError, yaml.YAMLError):
        with open(values_path, 'r') as f:
            return yaml.safe_load(f.read())

    return {}

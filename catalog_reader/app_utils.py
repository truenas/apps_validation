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
        'timezones': {'Asia/Saigon': 'Asia/Saigon', 'Asia/Damascus': 'Asia/Damascus'},
        'ip_choices': {'192.168.0.10': '192.168.0.10', '0.0.0.0': '0.0.0.0'},
        'certificates': [],
        'certificate_authorities': [],
        'system.general.config': {'timezone': 'America/Los_Angeles'},
        'gpu_choices': {}
    }


def get_app_basic_details(app_path: str) -> dict:
    # This just retrieves app name and app version from app path
    with contextlib.suppress(FileNotFoundError, yaml.YAMLError, KeyError):
        with open(os.path.join(app_path, 'app.yaml'), 'r') as f:
            app_config = yaml.safe_load(f.read())
        return {k: app_config.get(k) for k in ('lib_version', 'lib_version_hash')} | {
            k: app_config[k] for k in ('name', 'train', 'version')
        }

    return {}


def get_values(values_path: str) -> dict:
    with contextlib.suppress(FileNotFoundError, yaml.YAMLError):
        with open(values_path, 'r') as f:
            return yaml.safe_load(f.read())

    return {}


def get_human_version(app_version: str, version: str) -> str:
    return f'{app_version}_{version}' if app_version != version else version

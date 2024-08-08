from datetime import datetime


APP_VERSION = 'custom'
VERSION = '1.0.0'


def get_version_details() -> dict:
    """
    This is basically a stub which will be used in middleware to get version details of custom app
    """
    return {
        'app_metadata': {
            'name': 'custom-app',
            'train': 'stable',
            'version': VERSION,
            'app_version': APP_VERSION,
            'title': 'Custom App',
            'description': 'This is a custom app where user can use his/her '
                           'own docker compose file for deploying services',
            'home': '',
            'sources': [],
            'maintainers': [],
            'run_as_context': [],
            'capabilities': [],
            'host_mounts': [],
        },
        'version': VERSION,
        'human_version': f'{VERSION}_{APP_VERSION}',
        'supported': True,
        'healthy': True,
        'healthy_error': None,
        'location': None,
        'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }

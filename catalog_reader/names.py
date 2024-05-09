import typing


RECOMMENDED_APPS_FILENAME = 'recommended_apps.yaml'
TO_KEEP_VERSIONS = 'to_keep_versions.yaml'
UPGRADE_STRATEGY_FILENAME = 'upgrade_strategy'


def get_app_library_dir_name_from_version(version: str) -> str:
    return f'v{version.replace(".", "_")}'


def get_base_library_dir_name_from_version(version: typing.Optional[str]) -> str:
    return f'base_v{version.replace(".", "_")}' if version else ''

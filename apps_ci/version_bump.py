from pathlib import Path

from apps_exceptions import AppDoesNotExist, ValidationErrors


def map_renovate_bump_type(bump: str) -> str:
    return bump if bump in ('patch', 'minor', 'major') else 'patch'


def is_valid_version(version: str) -> bool:
    return isinstance(version, str) and version.count('.') == 2


def bump_version(version: str, bump: str) -> str:
    parts = version.split('.')
    if len(parts) != 3:
        raise ValueError(f'Invalid version {version!r}')
    match bump:
        case 'patch':
            parts[2] = str(int(parts[2]) + 1)
        case 'minor':
            parts[1] = str(int(parts[1]) + 1)
            parts[2] = '0'
        case 'major':
            parts[0] = str(int(parts[0]) + 1)
            parts[1] = '0'
            parts[2] = '0'

    return '.'.join(parts)


def rename_versioned_dir(version: str, new_version: str, train_name: str, app_dir: Path) -> None:
    verrors = ValidationErrors()

    if not is_valid_version(version) or not is_valid_version(new_version):
        verrors.add('version_bump', f'Invalid version {version!r} or {new_version!r}')
    verrors.check()

    if not app_dir.is_dir():
        raise AppDoesNotExist(app_dir)

    dir_base = app_dir / 'templates/library' / train_name / app_dir.name
    curr_versioned_dir = dir_base / f'v{version.replace(".", "_")}'
    new_versioned_dir = dir_base / f'v{new_version.replace(".", "_")}'
    if not curr_versioned_dir.is_dir():
        return

    if new_versioned_dir.is_dir():
        verrors.add('version_bump', f'App {app_dir.name!r} library with version {new_version!r} already exists')
    verrors.check()

    curr_versioned_dir.rename(new_versioned_dir)

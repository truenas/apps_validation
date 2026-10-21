def map_renovate_bump_type(bump: str) -> str:
    return bump if bump in ('patch', 'minor', 'major', '') else 'patch'


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

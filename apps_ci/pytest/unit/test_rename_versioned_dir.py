import pytest

from apps_ci.version_bump import bump_version


@pytest.mark.parametrize('version, bump, expected', [
    (
        '1.0.0',
        'minor',
        '1.1.0'
    ),
    (
        '1.0.0',
        'major',
        '2.0.0'
    ),
    (
        '1.0.0',
        'patch',
        '1.0.1'
    )
])
def test_bump_version(version, bump, expected):
    result = bump_version(version, bump)
    assert result == expected


def test_bump_version_Fail():
    with pytest.raises(ValueError):
        bump_version('1.0', 'minor')

import pytest

from apps_exceptions import ValidationErrors
from apps_validation.portals import validate_portals_and_notes


@pytest.mark.parametrize('data, should_work', [
    (
        {
            'x-portals': [{'host': '0.0.0.0', 'name': 'Web UI', 'path': '/web', 'port': 32400, 'scheme': 'http'}],
            'x-notes': '# A test note'
        },
        True
    ),
    (
        {
            'x-portals': [{'host': '0.0.0.0', 'name': 'Web UI', 'path': '/web', 'scheme': 'http'}],
            'x-notes': '# A test note'
        },
        False
    ),
    (
        {
            'x-portals': [{'host': '0.0.0.0', 'name': 'Web UI', 'path': '/web', 'port': 32400, 'scheme': 'http'}]
        },
        True
    ),
    (
        {
            'x-portals': [{'host': '0.0.0.0', 'name': 'Web UI', 'path': '/web', 'port': 32400, 'scheme': 'http'}],
            'x-notes': 123
        },
        False
    ),
    (
        {
            'x-portals': [{'host': '0.0.0.0', 'name': 'Web UI', 'path': '/web', 'port': '32400', 'scheme': 'http'}],
            'x-notes': '# A test note'
        },
        False
    )
])
def test_validate_portals_and_notes(data, should_work):
    if should_work:
        assert validate_portals_and_notes('test', data) is None
    else:
        with pytest.raises(ValidationErrors):
            validate_portals_and_notes('test', data)

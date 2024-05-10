import pytest

from apps_schema.attrs import get_schema
from apps_exceptions import ValidationErrors


@pytest.mark.parametrize('schema,should_work', [
    (
        {
            'type': 'dict',
            'attrs': []
        },
        True
    ),
    (
        {
            'type': 'dict',
            'attrs': {}
        },
        False
    ),
    (
        {
            'type': 'list'
        },
        False
    ),
    (
        {
            'type': 'list',
            'items': []
        },
        True
    ),
    (
        {
            'type': 'list',
            'items': {}
        },
        False
    ),
    (
        {
            'type': 'string',
            'editable': True
        },
        True
    ),
    (
        {
            'type': 'string',
            'default': 'hello'
        },
        True
    ),
    (
        {
            'type': 'string',
            'default': 1
        },
        False
    ),
    (
        {
            'type': 'string',
            'editable': 'true'
        },
        False
    ),
    (
        {
            'type': 'string',
            'private': True
        },
        True
    ),
    (
        {
            'type': 'string',
            'private': 'true'
        },
        False
    ),
    (
        {
            'type': 'string',
            'max_length': 233
        },
        True
    ),
    (
        {
            'type': 'string',
            'max_length': '233'
        },
        False
    ),
    (
        {
            'type': 'string',
            'min_length': 233
        },
        True
    ),
    (
        {
            'type': 'string',
            'min_length': '233'
        },
        False
    ),
    (
        {
            'type': 'string',
            'valid_chars': '[a-z]*'
        },
        True
    ),
    (
        {
            'type': 'string',
            'valid_chars': ['a-z']
        },
        False
    ),
    (
        {
            'type': 'string', 'null': True
        },
        True
    ),
    (
        {
            'type': 'string',
            'null': 'true'
        }, False
    ),
    (
        {
            'type': 'string',
            'immutable': True
        },
        True
    ),
    (
        {
            'type': 'string',
            'immutable': 'true'
        },
        False
    ),
    (
        {
            'type': 'string',
            'required': True
        },
        True
    ),
    (
        {
            'type': 'string',
            'required': 'true'
        },
        False
    ),
    (
        {
            'type': 'string',
            'hidden': True
        },
        True
    ),
    (
        {
            'type': 'string',
            'hidden': 'true'
        },
        False
    ),
    (
        {
            'type': 'string',
            'show_if': 'true'
        },
        False
    ),
    (
        {
            'type': 'string',
            'show_if': [['hello', '=', 'world']]
        },
        True
    ),
    (
        {
            'type': 'string',
            'subquestions': []
        },
        True
    ),
    (
        {
            'type': 'string',
            'subquestions': {}
        },
        False
    ),
    (
        {
            'type': 'string',
            'show_subquestions_if': None
        }, False
    ),
    (
        {
            'type': 'string',
            'show_subquestions_if': None,
            'subquestions': []
        },
        True
    ),
    (
        {
            'type': 'string',
            'show_subquestions_if': 1,
            'subquestions': []
        },
        True
    ),
    (
        {
            'type': 'string',
            'show_subquestions_if': 'test',
            'subquestions': []
        },
        True
    ),
    (
        {
            'type': 'string',
            'show_subquestions_if': {},
            'subquestions': []
        },
        True
    ),
    (
        {
            'type': 'string',
            'show_subquestions_if': [],
            'subquestions': []
        },
        True
    ),
    (
        {
            'type': 'string',
            '$ui-ref': []
        },
        True
    ),
    (
        {
            'type': 'string',
            '$ui-ref': {}
        },
        False
    ),
    (
        {
            'type': 'string',
            '$ref': []
        },
        True
    ),
    (
        {
            'type': 'string',
            '$ref': {}
        },
        False
    ),
    (
        {
            'type': 'int',
            'min': 233,
            'max': 2311
        },
        True
    ),
    (
        {
            'type': 'int',
            'min': '233',
            'max': 2311
        },
        False
    ),
    (
        {
            'type': 'int',
            'min': 233,
            'max': '2311'
        },
        False
    ),
    (
        {
            'type': 'int',
            'default': 23
        },
        True
    ),
    (
        {
            'type': 'int',
            'default': '23'
        },
        False
    ),
    (
        {
            'type': 'ipaddr',
            'ipv4': True,
            'ipv6': False,
            'cidr': True
        },
        True
    ),
    (
        {
            'type': 'ipaddr',
            'ipv4': True,
            'ipv6': False,
            'cidr': 'true'
        },
        False
    ),
    (
        {
            'type': 'ipaddr',
            'ipv4': True,
            'ipv6': 'False',
            'cidr': True
        },
        False
    ),
    (
        {
            'type': 'ipaddr',
            'ipv4': 'True',
            'ipv6': False,
            'cidr': True
        },
        False
    ),
    (
        {
            'type': 'string',
            'enum': [{
                'value': 'test',
                'description': 'test'
            }]
        },
        True
    ),
    (
        {
            'type': 'string',
            'enum': [{
                'value': 'test',
                'description': 'test',
                'obj': {}
            }]
        },
        False
    ),
    (
        {
            'type': 'string',
            'enum': [{
                'value': 'test'
            }]
        },
        False
    ),
    (
        {
            'type': 'string',
            'enum': [{
                'key': 'value'
            }]
        },
        False
    ),
    (
        {
            'type': 'string',
            'enum': [{}]
        },
        False
    ),
    (
        {
            'type': 'hostpath'
        },
        True
    ),
    (
        {
            'type': 'hostpath',
            'default': '/root/'
        },
        True
    ),
    (
        {
            'type': 'hostpath',
            'default': 231
        },
        False
    ),
    (
        {
            'type': 'path'
        },
        True
    ),
    (
        {
            'type': 'path',
            'default': '/root/'
        },
        True
    ),
    (
        {
            'type': 'path',
            'default': 231
        },
        False
    ),
    (
        {
            'type': 'boolean'
        },
        True
    ),
    (
        {
            'type': 'boolean',
            'default': True
        },
        True
    ),
    (
        {
            'type': 'boolean',
            'default': 'true'
        },
        False
    ),
    (
        {
            'type': 'cron'
        },
        True
    ),
    (
        {
            'type': 'cron',
            'default': {}
        },
        True
    ),
    (
        {
            'type': 'cron',
            'default': []
        },
        False
    ),
    (
        {
            'type': 'uri'
        },
        True
    ),
    (
        {
            'type': 'uri',
            'default': 'http://www.google.com'
        },
        True
    ),
    (
        {
            'type': 'uri',
            'default': 2133
        },
        False
    ),
])
def test_schema_validation(schema, should_work):
    if not should_work:
        with pytest.raises(ValidationErrors):
            get_schema(schema).validate('')
    else:
        assert get_schema(schema).validate('') is None

# FIXME: Port validate_question test as well

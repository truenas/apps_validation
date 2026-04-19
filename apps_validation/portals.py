from jsonschema import validate as json_schema_validate, ValidationError as JsonValidationError

from apps_exceptions import ValidationErrors


IX_NOTES_KEY = 'x-notes'
IX_PORTAL_KEY = 'x-portals'
IX_ACTION_REQUIRED_KEY = 'x-action-required'
VALIDATION_SCHEMA = {
    '$schema': 'https://json-schema.org/draft/2020-12/schema',
    'type': 'object',
    'properties': {
        'x-action-required': {
            'type': ['boolean', 'null'],
        },
        'x-portals': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'name': {
                        'type': 'string',
                        'minLength': 1,
                    },
                    'path': {
                        'type': 'string',
                        'pattern': '^/.*'
                    },
                    'scheme': {
                        'type': 'string',
                        'enum': ['http', 'https'],
                    },
                    'host': {'type': 'string'},
                    'port': {'type': 'integer'},
                },
                'required': ['name', 'scheme', 'host', 'port'],
                'additionalProperties': False
            },
        },
        'x-notes': {
            'type': ['string', 'null'],
        }
    },
}


def validate_portals_and_notes(schema, data):
    verrors = ValidationErrors()

    try:
        json_schema_validate(data, VALIDATION_SCHEMA)
    except JsonValidationError as e:
        verrors.add(schema, f'Failed to validate rendered portal config: {e}')

    verrors.check()

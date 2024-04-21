from jsonschema import validate as json_schema_validate, ValidationError as JsonValidationError

from apps_validation.exceptions import ValidationErrors


class BaseSchema:

    DEFAULT_TYPE = NotImplementedError

    def __init__(self, include_subquestions_attrs=True, data=None):
        self.required = self.null = self.show_if = self.ref = self.ui_ref = self.type =\
            self.editable = self.hidden = self.default = self._schema_data = None
        self._skip_data_values = []
        if include_subquestions_attrs:
            self.subquestions = self.show_subquestions_if = None
        if data:
            self.initialize_values(data)

    def initialize_values(self, data):
        self._schema_data = data
        for key, value in filter(
            lambda k: hasattr(self, k[0]) and k[0] not in self._skip_data_values, data.items()
        ):
            setattr(self, key, value)

    def get_schema_str(self, schema):
        if schema:
            return f'{schema}.'
        return ''

    def validate(self, schema, data=None):
        if data:
            self.initialize_values(data)

        if not self._schema_data:
            raise Exception('Schema data must be initialized before validating schema')

        verrors = ValidationErrors()
        try:
            json_schema_validate(self._schema_data, self.json_schema())
        except JsonValidationError as e:
            verrors.add(schema, f'Failed to validate schema: {e}')

        verrors.check()

        if '$ref' in self._schema_data:
            for index, ref in enumerate(self._schema_data['$ref']):
                if not isinstance(ref, str):
                    verrors.add(f'{schema}.$ref.{index}', 'Must be a string')
                    continue

                feature_obj = None  # get_feature(ref) FIXME: Fix this import
                if not feature_obj:
                    continue
                try:
                    feature_obj.validate(self, f'{schema}.$ref.{index}')
                except ValidationErrors as e:
                    verrors.extend(e)

        verrors.check()

    def json_schema(self):
        schema = {
            'type': 'object',
            'properties': {
                'required': {
                    'type': 'boolean',
                },
                'null': {
                    'type': 'boolean',
                },
                'show_if': {
                    'type': 'array',
                },
                '$ref': {
                    'type': 'array',
                },
                '$ui-ref': {
                    'type': 'array',
                },
                'subquestions': {
                    'type': 'array',
                },
                'show_subquestions_if': {
                    'type': ['string', 'integer', 'boolean', 'object', 'array', 'null'],
                },
                'type': {
                    'type': 'string',
                },
                'editable': {
                    'type': 'boolean',
                },
                'immutable': {
                    'type': 'boolean',
                },
                'hidden': {
                    'type': 'boolean',
                },
            },
            'required': ['type'],
            'dependentRequired': {
                'show_subquestions_if': ['subquestions']
            }
        }
        if self.DEFAULT_TYPE:
            schema['properties']['default'] = {
                'type': [self.DEFAULT_TYPE] + (['null'] if self.null else [])
            }
        if hasattr(self, 'enum'):
            schema['properties']['enum'] = {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'value': {'type': [self.DEFAULT_TYPE] + (['null'] if self.null else [])},
                        'description': {'type': ['string', 'null']},
                    },
                    'additionalProperties': False,
                    'required': ['value', 'description']
                },
            }
        return schema

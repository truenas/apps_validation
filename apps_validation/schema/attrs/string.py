from .base import Schema


class StringSchema(Schema):
    DEFAULT_TYPE = 'string'

    def __init__(self, data):
        self.min_length = self.max_length = self.enum = self.private = self.valid_chars = self.valid_chars_error = None
        super().__init__(data=data)

    def json_schema(self):
        schema = super().json_schema()
        schema['properties'].update({
            'min_length': {
                'type': 'integer',
            },
            'max_length': {
                'type': 'integer',
            },
            'private': {
                'type': 'boolean',
            },
            'valid_chars': {
                'type': 'string',
            },
            'valid_chars_error': {
                'type': 'string'
            },
        })
        return schema


class TextFieldSchema(StringSchema):
    def __init__(self, data):
        super().__init__(data)
        self.max_length = 1024 * 1024

    def json_schema(self):
        schema = super().json_schema()
        schema['properties'].update({
            'max_length': {
                'type': 'integer',
                'const': 1024 * 1024,
            },
            'language': {
                'type': 'string',
                'enum': ['yaml', 'json', 'toml', 'text'],
            }
        })
        return schema

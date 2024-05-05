from .base import BaseSchema


class DictSchema(BaseSchema):
    DEFAULT_TYPE = 'object'
    SCHEMA_NAME = 'dict'

    def __init__(self, data):
        self.attrs = []
        self.additional_attrs = None
        super().__init__(data=data)
        self._skip_data_values = ['attrs']

    def initialize_values(self, data):
        from apps_schema.variable import Variable
        super().initialize_values(data)
        self.attrs = [Variable(d) for d in (data.get('attrs') or [])]

    def json_schema(self):
        schema = super().json_schema()
        schema['additionalProperties'] = bool(self.additional_attrs)
        schema['properties']['attrs'] = {'type': 'array'}
        schema['required'].append('attrs')
        # We do not validate nested children and hence do not add it in the
        # json schema as it makes it very complex to handle all the possibilities
        return schema


class CronSchema(BaseSchema):
    DEFAULT_TYPE = 'object'
    SCHEMA_NAME = 'cron'

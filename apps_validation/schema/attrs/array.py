from .base import BaseSchema


class ListSchema(BaseSchema):

    DEFAULT_TYPE = 'array'

    def __init__(self, data):
        self.items = []
        super().__init__(False, data=data)
        self._skip_data_values = ['items']

    def initialize_values(self, data):
        from apps_validation.schema.variable import Variable
        super().initialize_values(data)
        self.items = [Variable(d) for d in (data.get('items') or [])]

    def json_schema(self):
        schema = super().json_schema()
        schema['properties']['items'] = {'type': 'array'}
        schema['required'].append('items')
        return schema

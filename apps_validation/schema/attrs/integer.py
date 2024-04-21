from .base import BaseSchema


class IntegerSchema(BaseSchema):
    DEFAULT_TYPE = 'integer'

    def __init__(self, data):
        self.min = self.max = self.enum = None
        super().__init__(data=data)

    def json_schema(self):
        schema = super().json_schema()
        schema['properties'].update({
            'min': {
                'type': 'integer',
            },
            'max': {
                'type': 'integer',
            },
        })
        return schema

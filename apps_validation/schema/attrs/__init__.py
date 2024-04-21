from .array import ListSchema  # noqa
from .bool import BooleanSchema  # noqa
from .dictionary import CronSchema, DictSchema  # noqa
from .integer import IntegerSchema  # noqa
from .string import (
    HostPathSchema, HostPathDirSchema, HostPathFileSchema, IPAddrSchema, PathSchema, StringSchema,
    TextFieldSchema, URISchema,
)  # noqa
from .utils import ATTRIBUTES_SCHEMA  # noqa


def get_schema(schema_data):
    schema = None
    if not isinstance(schema_data, dict):
        return schema

    if schema_klass := ATTRIBUTES_SCHEMA.get(schema_data.get('type')):
        schema = schema_klass(data=schema_data)

    return schema

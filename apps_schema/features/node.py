from apps_schema.attrs import StringSchema

from .base import BaseFeature


class DefinitionNodeIPFeature(BaseFeature):

    NAME = 'definitions/node_bind_ip'
    VALID_SCHEMAS = [StringSchema]

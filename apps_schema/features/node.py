from apps_schema.attrs import IntegerSchema, StringSchema

from .base import BaseFeature


class DefinitionNodeIPFeature(BaseFeature):

    NAME = 'definitions/node_ip'
    VALID_SCHEMAS = [StringSchema]


class ValidationNodePortFeature(BaseFeature):

    NAME = 'validations/node_port'
    VALID_SCHEMAS = [IntegerSchema]

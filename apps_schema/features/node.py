from apps_schema.attrs import IntegerSchema, StringSchema

from .base import BaseFeature


class DefinitionNodeIPFeature(BaseFeature):

    NAME = 'definitions/nodeIP'
    VALID_SCHEMAS = [StringSchema]


class ValidationNodePortFeature(BaseFeature):

    NAME = 'validations/nodePort'
    VALID_SCHEMAS = [IntegerSchema]

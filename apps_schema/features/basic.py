from apps_schema.attrs import DictSchema, StringSchema

from .base import BaseFeature


class DefinitionGPUConfigurationFeature(BaseFeature):

    NAME = 'definitions/gpuConfiguration'
    VALID_SCHEMAS = [DictSchema]


class DefinitionTimezoneFeature(BaseFeature):

    NAME = 'definitions/timezone'
    VALID_SCHEMAS = [StringSchema]

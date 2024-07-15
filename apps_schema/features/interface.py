from apps_schema.attrs import DictSchema, StringSchema

from .base import BaseFeature


class NormalizeInterfaceConfiguration(BaseFeature):
    NAME = 'normalize/interface_configuration'
    VALID_SCHEMAS = [DictSchema]


class DefinitionInterfaceFeature(BaseFeature):

    NAME = 'definitions/interface'
    VALID_SCHEMAS = [StringSchema]

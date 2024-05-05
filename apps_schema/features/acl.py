from apps_schema.attrs import DictSchema

from .base import BaseFeature


class ACLFeature(BaseFeature):

    NAME = 'normalize/acl'
    VALID_SCHEMAS = [DictSchema]

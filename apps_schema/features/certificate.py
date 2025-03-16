from apps_schema.attrs import IntegerSchema

from .base import BaseFeature


class CertificateFeature(BaseFeature):

    NAME = 'definitions/certificate'
    VALID_SCHEMAS = [IntegerSchema]

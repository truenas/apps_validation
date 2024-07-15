from apps_schema.attrs import IntegerSchema

from .base import BaseFeature


class CertificateFeature(BaseFeature):

    NAME = 'definitions/certificate'
    VALID_SCHEMAS = [IntegerSchema]


class CertificateAuthorityFeature(BaseFeature):

    NAME = 'definitions/certificate_authority'
    VALID_SCHEMAS = [IntegerSchema]

from apps_schema.attrs import DictSchema, StringSchema

from .base import BaseFeature


class ContainerImageFeature(BaseFeature):

    NAME = 'validations/containerImage'
    VALID_SCHEMAS = [DictSchema]

    def _validate(self, verrors, schema_obj, schema_str):
        attrs = schema_obj.attrs
        for check_attr in ('repository', 'tag'):
            if check_attr not in attrs:
                verrors.add(f'{schema_str}.attrs', f'Variable {check_attr!r} must be specified.')
            elif not isinstance(attrs[attrs.index(check_attr)].schema, StringSchema):
                verrors.add(f'{schema_str}.attrs', f'Variable {check_attr!r} must be of string type.')

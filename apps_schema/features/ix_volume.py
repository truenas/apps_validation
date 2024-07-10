from apps_schema.attrs import DictSchema, StringSchema

from .base import BaseFeature


class IXVolumeFeature(BaseFeature):

    NAME = 'normalize/ix_volume'
    VALID_SCHEMAS = [DictSchema, StringSchema]

    def _validate(self, verrors, schema_obj, schema_str):
        if isinstance(schema_obj, StringSchema):
            return

        attrs = schema_obj.attrs
        if 'dataset_name' not in attrs:
            verrors.add(f'{schema_str}.attrs', 'Variable "dataset_name" must be specified.')
        elif not isinstance(attrs[attrs.index('dataset_name')].schema, StringSchema):
            verrors.add(f'{schema_str}.attrs', 'Variable "dataset_name" must be of string type.')

        if 'acl_entries' in attrs and not isinstance(attrs[attrs.index('acl_entries')].schema, DictSchema):
            verrors.add(f'{schema_str}.attrs', 'Variable "acl_entries" must be of dict type.')

        if 'properties' in attrs:
            index = attrs.index('properties')
            properties = attrs[index]
            properties_schema = properties.schema
            supported_props = {
                'recordsize': {
                    'valid_schema_type': [StringSchema],
                },
            }
            not_supported = set([str(v) for v in properties_schema.attrs]) - set(supported_props)
            if not_supported:
                verrors.add(
                    f'{schema_str}.attrs.{index}.attrs', f'{", ".join(not_supported)} properties are not supported'
                )

            for prop_index, prop in enumerate(properties_schema.attrs):
                if prop.name not in supported_props:
                    continue

                prop_schema = prop.schema
                check_prop = supported_props[prop.name]
                if not isinstance(prop_schema, tuple(check_prop['valid_schema_type'])):
                    verrors.add(
                        f'{schema_str}.attrs.{index}.attrs.{prop_index}',
                        f'{prop.name!r} must be of '
                        f'{", ".join([str(s) for s in check_prop["valid_schema_type"]])} type(s)'
                    )

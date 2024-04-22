from middlewared.plugins.update_.utils import can_update

from apps_validation.exceptions import ValidationErrors

from .names import RE_SCALE_VERSION
from .utils import validate_key_value_types


def validate_min_max_version_values(annotations_dict: dict, verrors: ValidationErrors, schema: str):
    validate_key_value_types(
        annotations_dict, (('min_scale_version', str, False), ('max_scale_version', str, False)), verrors, schema
    )

    if verrors:
        # No point in proceeding further
        return

    for version in filter(lambda v: v in annotations_dict, ['min_scale_version', 'max_scale_version']):
        if not RE_SCALE_VERSION.match(annotations_dict[version]):
            verrors.add(
                f'{schema}.{version}',
                f'Format of provided {version} value is not correct'
            )

    if (
        not verrors and all(version in annotations_dict for version in ['min_scale_version', 'max_scale_version']) and
        annotations_dict['min_scale_version'] != annotations_dict['max_scale_version'] and
        not can_update(annotations_dict['min_scale_version'], annotations_dict['max_scale_version'])
    ):
        verrors.add(schema, 'Provided min_scale_version is greater than provided max_scale_version')

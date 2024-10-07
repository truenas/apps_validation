import pytest

from apps_exceptions import ValidationErrors
from apps_validation.scale_version import validate_min_max_version_values


@pytest.mark.parametrize('annotations_dict, schema, expected_error', [
    (
        {
            'min_scale_version': '23.04',
            'max_scale_version': '24.04'
        },
        'charts.plex.versions.1.7.56',
        None
    ),
    (
        {
            'min_scale_version': '24.04',
            'max_scale_version': '22.04'
        },
        'charts.plex.versions.1.7.56',
        'Provided min_scale_version is greater than provided max_scale_version'
    ),
    (
        {
            'min_scale_version': '15',
            'max_scale_version': '22.04'
        },
        'charts.plex.versions.1.7.56',
        'Format of provided min_scale_version value is not correct'
    ),
    (
        {
            'min_scale_version': 24.04,
        },
        'charts.plex.versions.1.7.56',
        '\'min_scale_version\' value should be a \'str\''
    ),
    (
        {
            'min_scale_version': '22.04',
            'max_scale_version': '14'
        },
        'charts.plex.versions.1.7.56',
        'Format of provided max_scale_version value is not correct'
    ),
    (
        {
            'min_scale_version': '22.04',
            'max_scale_version': 24.05
        },
        'charts.plex.versions.1.7.56',
        '\'max_scale_version\' value should be a \'str\''
    ),
])
def test_validate_min_max_versions(annotations_dict, schema, expected_error):
    verrors = ValidationErrors()
    if expected_error:
        with pytest.raises(ValidationErrors) as ve:
            validate_min_max_version_values(annotations_dict, verrors, schema)
            verrors.check()
        assert ve.value.errors[0].errmsg == expected_error
    else:
        assert validate_min_max_version_values(annotations_dict, verrors, schema) is None

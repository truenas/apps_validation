import pytest

from apps_exceptions import CatalogDoesNotExist, ValidationErrors
from apps_validation.scripts.catalog_validate import validate


@pytest.mark.parametrize(
    "catalog_path, side_effect, expected_output, expected_exit_code",
    [
        (
            "/valid/path",
            None,
            None,
            None
        ),
        (
            "/invalid/path",
            CatalogDoesNotExist('/invalid/path'),
            "[\x1b[91mFAILED\x1b[0m]\tSpecified '/invalid/path' path does not exist",
            1
        ),
        (
            "/valid/path_with_errors",
            ValidationErrors([("error_field", "Sample validation error")]),
            "[\x1b[91mFAILED\x1b[0m]\tFollowing validation failures were found:\n"
            "[\x1b[91m0\x1b[0m]\t('error_field', 'Sample validation error')",
            1
        ),
    ]
)
def test_validate(mocker, capsys, catalog_path, side_effect, expected_output, expected_exit_code):
    mocker.patch('apps_validation.scripts.catalog_validate.validate_catalog', side_effect=side_effect)

    if expected_exit_code:
        with pytest.raises(SystemExit) as exc:
            validate(catalog_path)
        assert exc.value.code == expected_exit_code
    else:
        validate(catalog_path)

    if expected_output:
        captured = capsys.readouterr()
        assert expected_output in captured.out

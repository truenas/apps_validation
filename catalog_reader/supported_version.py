from apps_validation.schema.features import FEATURES


def version_supported(version_details: dict) -> bool:
    return not bool(set(version_details['required_features']) - set(FEATURES))

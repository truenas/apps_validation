import re


CACHED_CATALOG_FILE_NAME = 'catalog.json'
CACHED_VERSION_FILE_NAME = 'app_versions.json'
RE_SCALE_VERSION = re.compile(r'^(\d{2}\.\d{2}(?:\.\d)*(?:-?(?:RC|BETA)\.?\d?)?)$')  # 24.04 / 24.04.1 / 24.04-RC.1
RE_VERSION_PATTERN = re.compile(r'(\d{2}\.\d{2}(?:\.\d)*)')  # We are only interested in XX.XX here
VALID_TRAIN_REGEX = re.compile(r'^\w+[\w.-]*$')
WANTED_FILES_IN_ITEM_VERSION = {'questions.yaml', 'app-readme.md', 'Chart.yaml', 'README.md'}  # FIXME


def validate_key_value_types(data_to_check, mapping, verrors, schema):
    for key_mapping in mapping:
        if len(key_mapping) == 2:
            key, value_type, required = *key_mapping, True
        else:
            key, value_type, required = key_mapping

        if required and key not in data_to_check:
            verrors.add(f'{schema}.{key}', f'Missing required {key!r} key.')
        elif key in data_to_check and not isinstance(data_to_check[key], value_type):
            verrors.add(f'{schema}.{key}', f'{key!r} value should be a {value_type.__name__!r}')

def validate_key_value_types(data_to_check, mapping, verrors, schema):
    for key_mapping in mapping:
        key = key_mapping[0]
        value_type = key_mapping[1]
        required = key_mapping[2] if len(key_mapping) == 3 else True

        if required and key not in data_to_check:
            verrors.add(f'{schema}.{key}', f'Missing required {key!r} key.')
        elif key in data_to_check and not isinstance(data_to_check[key], value_type):
            verrors.add(f'{schema}.{key}', f'{key!r} value should be a {value_type.__name__!r}')

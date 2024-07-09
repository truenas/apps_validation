import markdown
import os
import typing
import yaml

from pkg_resources import parse_version

from apps_exceptions import ValidationErrors
from apps_validation.validate_app import validate_catalog_item
from apps_validation.validate_app_version import validate_catalog_item_version  # FIXME: rename this

from .app_utils import get_default_questions_context, get_app_details_base, get_human_version
from .git import get_last_updated_date
from .questions import normalize_questions
from .supported_version import version_supported


ITEM_KEYS = ['icon_url']


def get_app_details(
    item_location: str, questions_context: typing.Optional[dict] = None, options: typing.Optional[dict] = None
) -> dict:
    catalog_path = item_location.rstrip('/').rsplit('/', 2)[0]
    item = item_location.rsplit('/', 1)[-1]
    train = item_location.rsplit('/', 2)[-2]

    options = options or {}
    retrieve_versions = options.get('retrieve_versions', True)
    item_data = get_app_details_base()
    item_data.update({
        'location': item_location,
        'last_update': get_last_updated_date(catalog_path, item_location),
        'name': item,
        'title': item.capitalize(),
    })

    schema = f'{train}.{item}'
    try:
        validate_catalog_item(item_location, schema, train, False)
    except ValidationErrors as verrors:
        item_data['healthy_error'] = f'Following error(s) were found with {item!r}:\n'
        for verror in verrors:
            item_data['healthy_error'] += f'{verror[0]}: {verror[1]}'

        # If the item format is not valid - there is no point descending any further into versions
        if not retrieve_versions:
            item_data.pop('versions')
        return item_data

    item_data.update(get_app_details_impl(item_location, schema, questions_context, {
        'retrieve_latest_version': not retrieve_versions,
        'default_values_callable': options.get('default_values_callable'),
    }))
    unhealthy_versions = []
    desired_keys_mapping = {
        'maintainers': 'maintainers',
        'description': 'description',
        'title': 'title',
        'home': 'home',
        'sources': 'sources',
    }
    for k, v in sorted(item_data['versions'].items(), key=lambda v: parse_version(v[0]), reverse=True):
        if not v['healthy']:
            unhealthy_versions.append(k)
        else:
            app_metadata = v['app_metadata']
            for desired_key in list(desired_keys_mapping):
                if not item_data[desired_key]:
                    item_data[desired_key] = app_metadata[desired_keys_mapping[desired_key]]
                desired_keys_mapping.pop(desired_key)

            if not item_data['latest_version']:
                item_data['latest_version'] = k
                item_data['latest_app_version'] = app_metadata['app_version']
                item_data['latest_human_version'] = get_human_version(app_metadata['app_version'], k)

            if not item_data['app_readme']:
                item_data['app_readme'] = v['readme']

    if unhealthy_versions:
        item_data['healthy_error'] = f'Errors were found with {", ".join(unhealthy_versions)} version(s)'
    else:
        item_data['healthy'] = True
    if not retrieve_versions:
        item_data.pop('versions')

    return item_data


def get_app_details_impl(
    item_path: str, schema: str, questions_context: typing.Optional[dict], options: typing.Optional[dict]
) -> dict:
    # Each directory under item path represents a version of the item and we need to retrieve details
    # for each version available under the item
    retrieve_latest_version = options.get('retrieve_latest_version')
    item_data = {
        'categories': [],
        'icon_url': None,
        'screenshots': [],
        'tags': [],
        'versions': {},
    }
    with open(os.path.join(item_path, 'item.yaml'), 'r') as f:
        item_data.update(yaml.safe_load(f.read()))

    item_data.update({k: item_data.get(k) for k in ITEM_KEYS})

    for version in sorted(
        filter(lambda p: os.path.isdir(os.path.join(item_path, p)), os.listdir(item_path)),
        reverse=True, key=parse_version,
    ):
        catalog_path = item_path.rstrip('/').rsplit('/', 2)[0]
        version_path = os.path.join(item_path, version)
        item_data['versions'][version] = version_details = {
            'healthy': False,
            'supported': False,
            'healthy_error': None,
            'location': version_path,
            'last_update': get_last_updated_date(catalog_path, version_path),
            'required_features': [],
            'human_version': version,
            'version': version,
        }
        try:
            validate_catalog_item_version(version_details['location'], f'{schema}.{version}')
        except ValidationErrors as verrors:
            version_details['healthy_error'] = f'Following error(s) were found with {schema}.{version!r}:\n'
            for verror in verrors:
                version_details['healthy_error'] += f'{verror[0]}: {verror[1]}'

            # There is no point in trying to see what questions etc the version has as it's invalid
            continue

        version_details.update({
            'healthy': True,
            **get_app_version_details(version_details['location'], questions_context)
        })
        if retrieve_latest_version:
            break

    return item_data


def get_app_version_details(
    version_path: str, questions_context: typing.Optional[dict], options: typing.Optional[dict] = None
) -> dict:
    version_data = {'location': version_path, 'required_features': set()}
    for key, filename, parser in (
        ('app_metadata', 'app.yaml', yaml.safe_load),
        ('schema', 'questions.yaml', yaml.safe_load),
        ('readme', 'README.md', markdown.markdown),
        ('changelog', 'CHANGELOG.md', markdown.markdown),
    ):
        if os.path.exists(os.path.join(version_path, filename)):
            with open(os.path.join(version_path, filename), 'r') as f:
                version_data[key] = parser(f.read())
        else:
            version_data[key] = None

    # We will normalise questions now so that if they have any references, we render them accordingly
    # like a field referring to available interfaces on the system
    normalize_questions(version_data, questions_context or get_default_questions_context())

    version_data.update({
        'supported': version_supported(version_data),
        'required_features': list(version_data['required_features']),
    })
    if options and options.get('default_values_callable'):
        version_data['values'] = options['default_values_callable'](version_data)

    app_metadata = version_data['app_metadata']
    # TODO: See if this needs to change for our adaptation of ix-chart
    version_data.update({
        'human_version': get_human_version(app_metadata['app_version'], app_metadata['version']),
        'version': app_metadata['version'],
    })

    return version_data

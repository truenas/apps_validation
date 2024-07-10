import itertools

from .questions_util import ACL_QUESTION, get_custom_portal_question, IX_VOLUMES_ACL_QUESTION


CUSTOM_PORTALS_ENABLE_KEY = 'enableIXPortals'
CUSTOM_PORTAL_GROUP_KEY = 'iXPortalsGroupName'  # FIXME: Talk to Stavros if this is even valid now


def normalize_questions(version_data: dict, context: dict) -> None:
    version_data['required_features'] = set()
    version_data['schema']['questions'].extend(
        [
            get_custom_portal_question(version_data['schema'][CUSTOM_PORTAL_GROUP_KEY])
        ] if version_data['schema'].get(CUSTOM_PORTALS_ENABLE_KEY) else []
    )
    for question in version_data['schema']['questions']:
        normalize_question(question, version_data, context)
    version_data['required_features'] = list(version_data['required_features'])


def normalize_question(question: dict, version_data: dict, context: dict) -> None:
    schema = question['schema']
    for attr in itertools.chain(*[schema.get(k, []) for k in ('attrs', 'items', 'subquestions')]):
        normalize_question(attr, version_data, context)

    if '$ref' not in schema:
        return

    data = {}
    for ref in schema['$ref']:
        version_data['required_features'].add(ref)
        if ref == 'definitions/interface':
            # FIXME: We should probably move this logic to feature class
            data['enum'] = [
                {'value': i, 'description': f'{i!r} Interface'} for i in context['nic_choices']
            ]
        elif ref == 'definitions/gpuConfiguration':
            data['attrs'] = [
                {
                    'variable': gpu,
                    'label': f'GPU Resource ({gpu})',
                    'description': 'Please enter the number of GPUs to allocate',
                    'schema': {
                        'type': 'int',
                        'max': int(quantity),
                        'enum': [
                            {'value': i, 'description': f'Allocate {i!r} {gpu} GPU'}
                            for i in range(int(quantity) + 1)
                        ],
                        'default': 0,
                    }
                } for gpu, quantity in context['gpus'].items()
            ]
        elif ref == 'definitions/timezone':
            data.update({
                'enum': [{'value': t, 'description': f'{t!r} timezone'} for t in sorted(context['timezones'])],
                'default': context['system.general.config']['timezone']
            })
        elif ref == 'definitions/nodeIP':
            data['default'] = context['node_ip']
        elif ref == 'definitions/certificate':
            get_cert_ca_options(schema, data, {'value': None, 'description': 'No Certificate'})
            data['enum'] += [
                {'value': i['id'], 'description': f'{i["name"]!r} Certificate'}
                for i in context['certificates']
            ]
        elif ref == 'definitions/certificateAuthority':
            get_cert_ca_options(schema, data, {'value': None, 'description': 'No Certificate Authority'})
            data['enum'] += [{'value': None, 'description': 'No Certificate Authority'}] + [
                {'value': i['id'], 'description': f'{i["name"]!r} Certificate Authority'}
                for i in context['certificate_authorities']
            ]
        elif ref == 'definitions/port':
            data['enum'] = [{'value': None, 'description': 'No Port Selected'}] if schema.get('null') else []
            data['enum'] += [
                {'value': i, 'description': f'{i!r} Port'}
                for i in filter(
                    lambda p: schema.get('min', 9000) <= p <= schema.get('max', 65534),
                    context['unused_ports']
                )
            ]
        elif ref == 'normalize/acl':
            data['attrs'] = ACL_QUESTION
        elif ref == 'normalize/ix_volume':
            if schema['type'] == 'dict' and any(i['variable'] == 'acl_entries' for i in schema['attrs']):
                # get index of acl_entries from attrs
                acl_index = next(i for i, v in enumerate(schema['attrs']) if v['variable'] == 'acl_entries')
                # insert acl question before acl_entries
                schema['attrs'][acl_index]['schema']['attrs'] = IX_VOLUMES_ACL_QUESTION

    schema.update(data)


def get_cert_ca_options(schema: dict, data: dict, default_entry: dict):
    if schema.get('null', True):
        data.update({
            'enum': [default_entry],
            'default': None,
            'null': True,
        })
    else:
        data.update({
            'enum': [],
            'required': True,
        })

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
        elif ref == 'definitions/gpu_configuration':
            # How we will go about this is the following:
            # If user has only nvidia gpus and we are able to retrieve nvidia gpu's uuid
            # we will allow user to select any of the available nvidia gpu
            # If user has any other GPU apart from nvidia vendor, he will have to passthrough all available gpus
            # If user has nvidia + other gpu's, then we can show a boolean or a string enum
            # highlighting the nvidia bits
            gpu_choices = [entry for entry in context['gpu_choices'] if entry['gpu_details']['available_to_host']]
            show_all_gpus_flag = any(
                g['vendor'] != 'NVIDIA' or not g['vendor_specific_config'].get('uuid') for g in gpu_choices
            )
            show_nvidia_selection = any(
                g['vendor'] == 'NVIDIA' and g['vendor_specific_config'].get('uuid') for g in gpu_choices
            )
            data['attrs'] = [
                {
                    'variable': 'use_all_gpus',
                    'label': 'Passthrough available (non-NVIDIA) GPUs',
                    'description': 'Please select this option to passthrough all (non-NVIDIA) GPUs to the app',
                    'schema': {
                        'type': 'boolean',
                        'default': False,
                        'hidden': not show_all_gpus_flag,
                    }
                },
                {
                    'variable': 'nvidia_gpu_selection',
                    'label': 'Select NVIDIA GPU(s)',
                    'description': 'Please select the NVIDIA GPU(s) to passthrough to the app',
                    'schema': {
                        'type': 'dict',
                        'additional_attrs': True,
                        'hidden': not show_nvidia_selection,
                        'attrs': [
                            {
                                'variable': gpu['gpu_details']['addr']['pci_slot'],
                                'label': gpu['description'],
                                'description': f'NVIDIA gpu {gpu["vendor_specific_config"]["uuid"]}',
                                'schema': {
                                    'type': 'dict',
                                    'attrs': [
                                        {
                                            'variable': 'uuid',
                                            'schema': {
                                                'type': 'string',
                                                'default': gpu['vendor_specific_config']['uuid'],
                                                'hidden': True,
                                            }
                                        },
                                        {
                                            'variable': 'use_gpu',
                                            'label': 'Use this GPU',
                                            'description': 'Use this GPU for the app',
                                            'schema': {
                                                'type': 'boolean',
                                                'default': False,
                                            }
                                        }
                                    ],
                                }
                            }
                            for gpu in (gpu_choices if show_nvidia_selection else [])
                            if gpu['vendor'] == 'NVIDIA' and gpu['vendor_specific_config'].get('uuid')
                        ]
                    },
                },
            ]

        elif ref == 'definitions/timezone':
            data.update({
                'enum': [{'value': t, 'description': f'{t!r} timezone'} for t in sorted(context['timezones'])],
                'default': context['system.general.config']['timezone']
            })
        elif ref == 'definitions/node_bind_ip':
            data.update({
                'default': '0.0.0.0',
                'enum': [{'value': i, 'description': f'{i!r} IP Address'} for i in context['ip_choices']],
            })
        elif ref == 'definitions/certificate':
            get_cert_ca_options(schema, data, {'value': None, 'description': 'No Certificate'})
            data['enum'] += [
                {'value': i['id'], 'description': f'{i["name"]!r} Certificate'}
                for i in context['certificates']
            ]
        elif ref == 'definitions/certificate_authority':
            get_cert_ca_options(schema, data, {'value': None, 'description': 'No Certificate Authority'})
            data['enum'] += [{'value': None, 'description': 'No Certificate Authority'}] + [
                {'value': i['id'], 'description': f'{i["name"]!r} Certificate Authority'}
                for i in context['certificate_authorities']
            ]
        elif ref == 'definitions/port':
            data['enum'] = [{'value': None, 'description': 'No Port Selected'}] if schema.get('null') else []
            data['enum'] += [
                {'value': i, 'description': f'{i!r} Port'}
                for i in context['unused_ports']
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

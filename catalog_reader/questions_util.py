ACL_QUESTION = [
    {
        'variable': 'path',
        'label': 'Host Path',
        'description': 'Host Path to perform ACL',
        'schema': {
            'type': 'hostpath',
            'required': True,
            'empty': False,
        }
    },
    {
        'variable': 'entries',
        'label': 'ACL Entries',
        'description': 'ACL Entries',
        'schema': {
            'type': 'list',
            'items': [{
                'variable': 'acl_entry',
                'label': 'ACL Entry',
                'schema': {
                    'type': 'dict',
                    'attrs': [
                        {
                            'variable': 'id_type',
                            'label': 'ID Type',
                            'schema': {
                                'type': 'string',
                                'enum': [
                                    {'value': 'USER', 'description': 'Entry is for a USER'},
                                    {'value': 'GROUP', 'description': 'Entry is for a GROUP'},
                                ],
                                'default': 'USER',
                            }
                        },
                        {
                            'variable': 'id',
                            'label': 'ID',
                            'description': 'Make sure to check the ID value is correct and aligns with '
                                           'RunAs user context of the application',
                            'schema': {
                                'type': 'int',
                                'required': True,
                                'min': 0,
                            }
                        },
                        {
                            'variable': 'access',
                            'label': 'Access',
                            'schema': {
                                'type': 'string',
                                'enum': [
                                    {'value': 'READ', 'description': 'Read Access'},
                                    {'value': 'MODIFY', 'description': 'Modify Access'},
                                    {'value': 'FULL_CONTROL', 'description': 'FULL_CONTROL Access'},
                                ],
                            }
                        }
                    ],
                }
            }]
        }
    },
    {
        'variable': 'options',
        'label': 'ACL Options',
        'schema': {
            'type': 'dict',
            'attrs': [
                {
                    'variable': 'force',
                    'label': 'Force Flag',
                    'description': 'Enabling `Force` applies ACL even if the path has existing data',
                    'schema': {
                        'type': 'boolean',
                        'default': False,
                    }
                },
            ],
        },
    },
]
CUSTOM_PORTALS_KEY = 'ix_portals'
IX_VOLUMES_ACL_QUESTION = [
    {
        'variable': 'path',
        'label': 'Path',
        'description': 'Path to perform ACL',
        'schema': {
            'type': 'string',
            'hidden': True
        }
    },
    ACL_QUESTION[1],
    {
        'variable': 'options',
        'label': 'ACL Options',
        'schema': {
            'type': 'dict',
            'hidden': True,
            'attrs': [
                {
                    'variable': 'force',
                    'label': 'Force Flag',
                    'description': 'Enabling `Force` applies ACL even if the path has existing data',
                    'schema': {
                        'type': 'boolean',
                        'default': True,
                    }
                },
            ],
        },
    },
]


def get_custom_portal_question(group_name: str) -> dict:
    return {
        'variable': CUSTOM_PORTALS_KEY,
        'label': 'User Specified Web Portals',
        'description': 'User(s) can specify custom webUI portals',
        'group': group_name,
        'schema': {
            'type': 'list',
            'items': [{
                'variable': 'portalConfiguration',
                'label': 'Portal Configuration',
                'description': 'Configure WebUI Portal',
                'schema': {
                    'type': 'dict',
                    'attrs': [
                        {
                            'variable': 'portalName',
                            'label': 'Portal Name',
                            'description': 'Specify a UI Portal name to use which would be displayed in the UI',
                            'schema': {
                                'type': 'string',
                                'default': 'Web Portal',
                                'empty': False,
                            },
                        },
                        {
                            'variable': 'protocol',
                            'label': 'Protocol for Portal',
                            'description': 'Specify protocol for Portal',
                            'schema': {
                                'type': 'string',
                                'default': 'http',
                                'enum': [
                                    {'value': 'http', 'description': 'HTTP Protocol'},
                                    {'value': 'https', 'description': 'HTTPS Protocol'},
                                ],
                            },
                        },
                        {
                            'variable': 'useNodeIP',
                            'label': 'Use Node IP for Portal IP/Domain',
                            'schema': {
                                'type': 'boolean',
                                'default': True,
                            },
                        },
                        {
                            'variable': 'host',
                            'label': 'Portal IP/Domain',
                            'schema': {
                                'type': 'string',
                                'show_if': [['useNodeIP', '=', False]],
                                '$ref': ['definitions/nodeIP'],
                            },
                        },
                        {
                            'variable': 'port',
                            'label': 'Port',
                            'description': 'Specify port to be used for Portal access',
                            'schema': {
                                'type': 'int',
                                'max': 65535,
                                'default': 15000,
                            },
                        },
                        {
                            'variable': 'path',
                            'label': 'Path (optional - leave empty if not required)',
                            'description': 'Some app(s) might have a sub path i.e http://192.168.0.10:9000/api/',
                            'schema': {
                                'type': 'string',
                            },
                        },
                    ],
                },
            }],
        },
    }

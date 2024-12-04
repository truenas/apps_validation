import pytest

from catalog_reader.questions import normalize_question
from catalog_reader.questions_util import ACL_QUESTION, IX_VOLUMES_ACL_QUESTION


VERSION_DATA = {
    'location': '/mnt/mypool/ix-applications/catalogs/github_com_truenas_charts_git_master/charts/syncthing/1.0.14',
    'required_features': {
        'normalize/ixVolume',
        'validations/lockedHostPath',
    },
    'chart_metadata': {},
    'schema': {
        'variable': 'hostNetwork',
        'label': 'Host Network',
        'group': 'Networking',
    },
    'app_readme': 'there is not any',
    'detailed_readme': 'there is not any',
    'changelog': None,
}

GPU_CHOICES = [
    {
        'vendor': None,
        'description': 'ASPEED Technology, Inc. ASPEED Graphics Family',
        'error': None,
        'vendor_specific_config': {},
        'gpu_details': {
            'addr': {
              'pci_slot': '0000:03:00.0',
              'domain': '0000',
              'bus': '03',
              'slot': '00'
            },
            'description': 'ASPEED Technology, Inc. ASPEED Graphics Family',
            'devices': [
              {
                'pci_id': '1A03:2000',
                'pci_slot': '0000:03:00.0',
                'vm_pci_slot': 'pci_0000_03_00_0'
              }
            ],
            'vendor': None,
            'uses_system_critical_devices': True,
            'critical_reason': 'Critical devices found in same IOMMU group: 0000:03:00.0',
            'available_to_host': True
        },
        'pci_slot': '0000:03:00.0'
    },
    {
        'vendor': 'NVIDIA',
        'description': 'NVIDIA T400 4GB',
        'error': None,
        'vendor_specific_config': {
            'uuid': 'GPU-059f2adb-93bf-82f6-9f73-366a21bd00c7'
        },
        'gpu_details': {
            'addr': {
              'pci_slot': '0000:17:00.0',
              'domain': '0000',
              'bus': '17',
              'slot': '00'
            },
            'description': 'NVIDIA Corporation TU117GL [T400 4GB]',
            'devices': [
              {
                'pci_id': '10DE:1FF2',
                'pci_slot': '0000:17:00.0',
                'vm_pci_slot': 'pci_0000_17_00_0'
              },
              {
                'pci_id': '10DE:10FA',
                'pci_slot': '0000:17:00.1',
                'vm_pci_slot': 'pci_0000_17_00_1'
              }
            ],
            'vendor': 'NVIDIA',
            'uses_system_critical_devices': False,
            'critical_reason': None,
            'available_to_host': True
          },
        'pci_slot': '0000:17:00.0'
    },
    {
        'vendor': 'NVIDIA',
        'description': 'NVIDIA Corporation TU117GL [T400 4GB]',
        'error': 'Unable to locate GPU details from procfs',
        'vendor_specific_config': {},
        'gpu_details': {
            'addr': {
                'pci_slot': '0000:65:00.0',
                'domain': '0000',
                 'bus': '65',
                'slot': '00'
              },
            'description': 'NVIDIA Corporation TU117GL [T400 4GB]',
            'devices': [
                {
                  'pci_id': '10DE:1FF2',
                  'pci_slot': '0000:65:00.0',
                  'vm_pci_slot': 'pci_0000_65_00_0'
                },
                {
                  'pci_id': '10DE:10FA',
                  'pci_slot': '0000:65:00.1',
                  'vm_pci_slot': 'pci_0000_65_00_1'
                }
            ],
            'vendor': 'NVIDIA',
            'uses_system_critical_devices': False,
            'critical_reason': None,
            'available_to_host': False
          },
        'pci_slot': '0000:65:00.0'
    }
]

GPU_DETAIL = [entry for entry in GPU_CHOICES if entry['gpu_details']['available_to_host']]


@pytest.mark.parametrize('question, normalized_data, context', [
    (
        {
            'variable': 'datasetName',
            'label': 'Plots Volume Name',
            'schema': {
                'type': 'string',
                'hidden': True,
                '$ref': ['definitions/interface'],
            }
        },
        {
            'variable': 'datasetName',
            'label': 'Plots Volume Name',
            'schema': {
                'type': 'string',
                'hidden': True,
                '$ref': ['definitions/interface'],
                'enum': [],
            }
        },
        {
            'nic_choices': [],
        }
    ),
    (
        {
            'variable': 'datasetName',
            'label': 'Plots Volume Name',
            'schema': {
                'type': 'string',
                'hidden': True,
                '$ref': ['definitions/interface'],
            }
        },
        {
            'variable': 'datasetName',
            'label': 'Plots Volume Name',
            'schema': {
                'type': 'string',
                'hidden': True,
                '$ref': ['definitions/interface'],
                'enum': [
                    {
                        'value': 'ens0',
                        'description': "'ens0' Interface"
                    }
                ],
            }
        },
        {
            'nic_choices': ['ens0']
        }
    ),
    (
        {
            'variable': 'datasetName',
            'label': 'Plots Volume Name',
            'schema': {
                'type': 'string',
                'hidden': True,
            }
        },
        {
            'variable': 'datasetName',
            'label': 'Plots Volume Name',
            'schema': {
                'type': 'string',
                'hidden': True,
            }
        },
        {
            'nic_choices': [],
        }
    ),
    (
        {
            'variable': 'datasetName',
            'label': 'Plots Volume Name',
            'schema': {
                'type': 'string',
                'hidden': True,
                '$ref': ['definitions/gpu_configuration'],
            }
        },
        {
            'variable': 'datasetName',
            'label': 'Plots Volume Name',
            'schema': {
                'type': 'string',
                'hidden': True,
                '$ref': ['definitions/gpu_configuration'],
                'attrs': [
                    {
                        'variable': 'use_all_gpus',
                        'label': 'Passthrough available (non-NVIDIA) GPUs',
                        'description': 'Please select this option to passthrough all (non-NVIDIA) GPUs to the app',
                        'schema': {
                            'type': 'boolean',
                            'default': False,
                            'hidden': False,
                        }
                    },
                    {
                        'variable': 'kfd_device_exists',
                        'label': 'KFD Device Exists',
                        'schema': {
                            'type': 'boolean',
                            'default': False,
                            'hidden': True,
                        }
                    },
                    {
                        'variable': 'nvidia_gpu_selection',
                        'label': 'Select NVIDIA GPU(s)',
                        'description': 'Please select the NVIDIA GPU(s) to passthrough to the app',
                        'schema': {
                            'type': 'dict',
                            'additional_attrs': True,
                            'hidden': False,
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
                                for gpu in GPU_DETAIL
                                if gpu['vendor'] == 'NVIDIA' and gpu['vendor_specific_config'].get('uuid')
                            ]
                        },
                    },
                ],
            }
        },
        {
            'gpu_choices': GPU_CHOICES
        }
    ),
    (
        {
            'variable': 'datasetName',
            'label': 'Plots Volume Name',
            'schema': {
                'type': 'string',
                'hidden': True,
                '$ref': ['definitions/timezone'],
            }
        },
        {
            'variable': 'datasetName',
            'label': 'Plots Volume Name',
            'schema': {
                'type': 'string',
                'hidden': True,
                '$ref': ['definitions/timezone'],
                'enum': [
                    {
                        'value': 'Asia/Damascus',
                        'description': "'Asia/Damascus' timezone",
                    },
                    {
                        'value': 'Asia/Saigon',
                        'description': "'Asia/Saigon' timezone",
                    }
                ],
                'default': 'America/Los_Angeles',
            }
        },
        {
            'timezones': {
                'Asia/Saigon': 'Asia/Saigon',
                'Asia/Damascus': 'Asia/Damascus',
            },
            'system.general.config': {
                'timezone': 'America/Los_Angeles',
            }
        }
    ),
    (
        {
            'variable': 'datasetName',
            'label': 'Plots Volume Name',
            'schema': {
                'type': 'string',
                'hidden': True,
                '$ref': ['definitions/node_bind_ip'],
            }
        },
        {
            'variable': 'datasetName',
            'label': 'Plots Volume Name',
            'schema': {
                'type': 'string',
                'hidden': True,
                '$ref': ['definitions/node_bind_ip'],
                'default': '0.0.0.0',
                'enum': [
                    {
                        'value': '192.168.0.10',
                        'description': "'192.168.0.10' IP Address"
                    }
                ]
            }
        },
        {
            'ip_choices': {'192.168.0.10'}
        }
    ),
    (
        {
            'variable': 'datasetName',
            'label': 'Plots Volume Name',
            'schema': {
                'type': 'string',
                'hidden': True,
                '$ref': ['definitions/certificate'],
            }
        },
        {
            'variable': 'datasetName',
            'label': 'Plots Volume Name',
            'schema': {
                'type': 'string',
                'hidden': True,
                '$ref': ['definitions/certificate'],
                'enum': [{'value': None, 'description': 'No Certificate'}],
                'default': None,
                'null': True
            }
        },
        {
            'certificates': [],
        }
    ),
    (
        {
            'variable': 'datasetName',
            'label': 'Plots Volume Name',
            'schema': {
                'type': 'string',
                'hidden': True,
                '$ref': ['definitions/certificate_authority'],
            }
        },
        {
            'variable': 'datasetName',
            'label': 'Plots Volume Name',
            'schema': {
                'type': 'string',
                'hidden': True,
                '$ref': ['definitions/certificate_authority'],
                'enum': [
                    {'value': None, 'description': 'No Certificate Authority'},
                    {'value': None, 'description': 'No Certificate Authority'}
                ],
                'default': None,
                'null': True
            }
        },
        {
            'certificate_authorities': [],
        }
    ),
    (
        {
            'variable': 'datasetName',
            'label': 'Plots Volume Name',
            'schema': {
                'type': 'string',
                'hidden': True,
                '$ref': ['definitions/port'],
            }
        },
        {
            'variable': 'datasetName',
            'label': 'Plots Volume Name',
            'schema': {
                'type': 'string',
                'hidden': True,
                '$ref': ['definitions/port'],
                'min': 1,
                'max': 65535
            }
        },
        {
            'port': [],
        }
    ),
    (
        {
            'variable': 'datasetName',
            'label': 'Plots Volume Name',
            'schema': {
                'type': 'string',
                'hidden': True,
                '$ref': ['normalize/acl'],
            }
        },
        {
            'variable': 'datasetName',
            'label': 'Plots Volume Name',
            'schema': {
                'type': 'string',
                'hidden': True,
                '$ref': ['normalize/acl'],
                'attrs': ACL_QUESTION
            }
        },
        {
            'acl': []
        }
    ),
    (
        {
            'variable': 'datasetName',
            'label': 'Plots Volume Name',
            'schema': {
                'type': 'dict',
                '$ref': ['normalize/ix_volume'],
                'attrs': [
                    {
                        'variable': 'acl_entries',
                        'label': 'ACL Configuration',
                        'schema': {
                            'type': 'dict',
                            'attrs': []
                        }
                    }
                ]
            }
        },
        {
            'variable': 'datasetName',
            'label': 'Plots Volume Name',
            'schema': {
                'type': 'dict',
                '$ref': ['normalize/ix_volume'],
                'attrs': [
                    {
                        'variable': 'acl_entries',
                        'label': 'ACL Configuration',
                        'schema': {
                            'type': 'dict',
                            'attrs': IX_VOLUMES_ACL_QUESTION
                        }
                    }
                ]
            }
        },
        {}
    ),
    (
        {
            'variable': 'datasetName',
            'label': 'Plots Volume Name',
            'schema': {
                'type': 'string',
                'hidden': True,
                '$ref': ['definitions/certificate'],
                'null': False
            }
        },
        {
            'variable': 'datasetName',
            'label': 'Plots Volume Name',
            'schema': {
                'type': 'string',
                'hidden': True,
                '$ref': ['definitions/certificate'],
                'null': False,
                'enum': [],
                'required': True
            }
        },
        {
            'certificates': [],
        }
    )
])
def test_normalize_question(question, normalized_data, context):
    normalize_question(question, VERSION_DATA, context)
    assert question == normalized_data

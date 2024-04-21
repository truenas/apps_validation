CATALOG_JSON_SCHEMA = {
    'type': 'object',
    'patternProperties': {
        '.*': {
            'type': 'object',
            'title': 'Train',
            'patternProperties': {
                '.*': {
                    'type': 'object',
                    'title': 'Item',
                    'properties': {
                        'name': {
                            'type': 'string',
                            'title': 'Name',
                        },
                        'categories': {
                            'type': 'array',
                            'items': {
                                'type': 'string'
                            },
                        },
                        'app_readme': {
                            'type': 'string',
                        },
                        'location': {
                            'type': 'string',
                        },
                        'healthy': {
                            'type': 'boolean',
                        },
                        'healthy_error': {
                            'type': ['string', 'null'],
                        },
                        'last_update': {
                            'type': 'string',
                            'pattern': r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$',
                        },
                        'latest_version': {
                            'type': 'string',
                        },
                        'latest_app_version': {
                            'type': 'string',
                        },
                        'latest_human_version': {
                            'type': 'string',
                        },
                        'description': {
                            'type': ['string', 'null'],
                        },
                        'title': {
                            'type': 'string',
                        },
                        'icon_url': {
                            'type': ['string', 'null'],
                        },
                        'maintainers': {
                            'type': 'array',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'name': {'type': 'string'},
                                    'url': {'type': ['string', 'null']},
                                    'email': {'type': 'string'}
                                },
                                'required': ['name', 'email'],
                            }
                        },
                        'home': {
                            'type': 'string',
                        },
                        'tags': {
                            'type': 'array',
                            'items': {
                                'type': 'string',
                            }
                        },
                        'screenshots': {
                            'type': 'array',
                            'items': {
                                'type': 'string',
                            }
                        },
                        'sources': {
                            'type': 'array',
                            'items': {
                                'type': 'string',
                            }
                        },
                    },
                    'required': [
                        'name', 'categories', 'location', 'healthy', 'icon_url',
                        'latest_version', 'latest_app_version', 'latest_human_version',
                        'last_update', 'recommended', 'healthy_error', 'maintainers',
                        'home', 'tags', 'sources', 'screenshots',
                    ],
                }
            }

        }
    }
}
METADATA_JSON_SCHEMA = {
    'type': 'object',
    'properties': {
        'runAsContext': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'description': {'type': 'string'},
                    'gid': {'type': 'integer'},
                    'groupName': {'type': 'string'},
                    'userName': {'type': 'string'},
                    'uid': {'type': 'integer'},
                },
                'required': ['description'],
            },
        },
        'capabilities': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'description': {'type': 'string'},
                    'name': {'type': 'string'},
                },
                'required': ['description', 'name'],
            },
        },
        'hostMounts': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'description': {'type': 'string'},
                    'hostPath': {'type': 'string'},
                },
                'required': ['description', 'hostPath'],
            },
        },
    },
}
RECOMMENDED_APPS_JSON_SCHEMA = {
    'type': 'object',
    'patternProperties': {
        '.*': {
            'type': 'array',
            'items': {'type': 'string'},
        }
    },
}
VERSION_VALIDATION_SCHEMA = {
    'type': 'object',
    'title': 'Versions',
    'patternProperties': {
        '[0-9]+.[0-9]+.[0-9]+': {
            'type': 'object',
            'properties': {
                'healthy': {
                    'type': 'boolean',
                },
                'supported': {
                    'type': 'boolean',
                },
                'healthy_error': {
                    'type': ['string', 'null']
                },
                'location': {
                    'type': 'string',
                    'pattern': r'^(\/[a-zA-Z0-9_.-]+)+$'
                },
                'last_update': {
                    'type': 'string',
                    'pattern': '^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}$'
                },
                'required_features': {
                    'type': 'array',
                    'items': {
                        'type': 'string'
                    }
                },
                'human_version': {
                    'type': 'string'
                },
                'version': {
                    'type': 'string',
                    'pattern': '[0-9]+.[0-9]+.[0-9]+'
                },
                'chart_metadata': {
                    'type': 'object',
                    'properties': {
                        'name': {
                            'type': 'string'
                        },
                        'description': {
                            'type': 'string'
                        },
                        'annotations': {
                            'type': 'object'
                        },
                        'type': {
                            'type': 'string'
                        },
                        'version': {
                            'type': 'string',
                            'pattern': '[0-9]+.[0-9]+.[0-9]+'
                        },
                        'apiVersion': {
                            'type': 'string',
                        },
                        'appVersion': {
                            'type': 'string'
                        },
                        'kubeVersion': {
                            'type': 'string'
                        },
                        'app_readme': {'type': 'string'},
                        'detailed_readme': {'type': 'string'},
                        'changelog': {'type': ['string', 'null']},
                        'maintainers': {
                            'type': 'array',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'name': {'type': 'string'},
                                    'url': {'type': ['string', 'null']},
                                    'email': {'type': 'string'},
                                },
                                'required': ['name', 'email'],
                            }
                        },
                        'dependencies': {
                            'type': 'array',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'name': {'type': 'string'},
                                    'repository': {'type': 'string'},
                                    'version': {'type': 'string'}
                                }
                            }
                        },
                        'home': {'type': 'string'},
                        'icon': {'type': 'string'},
                        'sources': {
                            'type': 'array',
                            'items': {
                                'type': 'string'
                            }
                        },
                        'keywords': {
                            'type': 'array',
                            'items': {
                                'type': 'string'
                            }
                        },
                    }
                },
                'app_metadata': {
                    **METADATA_JSON_SCHEMA,
                    'type': ['object', 'null'],
                },
                'schema': {
                    'type': 'object',
                    'properties': {
                        'groups': {
                            'type': 'array',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'name': {
                                        'type': 'string'
                                    },
                                    'description': {
                                        'type': 'string'
                                    },
                                },
                                'required': ['description', 'name'],
                            }
                        },
                        'portals': {
                            'type': 'object'
                        },
                        'questions': {
                            'type': 'array',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'variable': {'type': 'string'},
                                    'label': {'type': 'string'},
                                    'group': {'type': 'string'},
                                    'schema': {
                                        'type': 'object',
                                        'properties': {
                                            'type': {'type': 'string'}
                                        },
                                        'required': ['type']
                                    }
                                }
                            }
                        }
                    },
                    'required': ['groups', 'questions']
                },
            },
            'required': [
                'healthy', 'supported', 'healthy_error', 'location', 'last_update', 'required_features',
                'human_version', 'version', 'chart_metadata', 'app_metadata', 'schema',
            ],
        },
    },
    'additionalProperties': False
}  # FIXME: See if all keys port

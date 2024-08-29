from distutils.core import setup
from setuptools import find_packages

VERSION = '0.1'

setup(
    name='apps_validation',
    description='Validate TrueNAS Apps Catalog',
    version=VERSION,
    include_package_data=True,
    packages=find_packages(include=[
        'apps_ci',
        'apps_ci.*',
        'apps_exceptions',
        'apps_exceptions.*',
        'apps_schema',
        'apps_schema.*',
        'apps_validation',
        'apps_validation.*',
        'catalog_reader',
        'catalog_reader.*',
        'catalog_templating',
        'catalog_templating.*',
    ]),
    license='GNU3',
    platforms='any',
    entry_points={
        'console_scripts': [
            'app_bump_version = apps_ci.scripts.bump_version:main',
            'apps_catalog_hash_generate = catalog_reader.scripts.apps_hashes:main',
            'apps_catalog_update = apps_ci.scripts.catalog_update:main',
            'apps_catalog_validate = apps_validation.scripts.catalog_validate:main',
            'apps_dev_charts_validate = apps_validation.scripts.dev_apps_validate:main',  # TODO: Remove apps_prefix
            'apps_render_app = catalog_templating.scripts.render_compose:main',
        ],
    },
)

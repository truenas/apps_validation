from distutils.core import setup
from setuptools import find_packages

VERSION = '0.1'

setup(
    name='apps_validation',
    description='Validate TrueNAS Apps Catalog',
    version=VERSION,
    include_package_data=True,
    packages=find_packages(),
    license='GNU3',
    platforms='any',
    entry_points={
        'console_scripts': [
            'apps_catalog_update = catalog_validation.scripts.catalog_update:main',
            'apps_catalog_validate = catalog_validation.scripts.catalog_validate:main',
            'apps_dev_charts_validate = apps_validation.scripts.dev_apps_validate:main',  # TODO: Remove apps_prefix
        ],
    },
)

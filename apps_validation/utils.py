import re


CACHED_CATALOG_FILE_NAME = 'catalog.json'
CACHED_VERSION_FILE_NAME = 'app_versions.json'
RE_VERSION_PATTERN = re.compile(r'(\d{2}\.\d{2}(?:\.\d)*)')  # We are only interested in XX.XX here
WANTED_FILES_IN_ITEM_VERSION = {'questions.yaml', 'app-readme.md', 'Chart.yaml', 'README.md'}  # FIXME

import contextlib
import os
import pathlib
import re
import yaml

from .hash_utils import get_hash_of_directory
from .names import get_library_path, get_library_hashes_path


RE_VERSION = re.compile(r'^\d+.\d+\.\d+$')
EXCLUDED_PATTERNS = [
    "tests/",
    "__pycache__/",
]


def get_library_hashes(library_path: str) -> dict:
    """
    This reads from library hashes file and returns the hashes
    """
    with contextlib.suppress(FileNotFoundError, yaml.YAMLError):
        with open(get_library_hashes_path(library_path), 'r') as f:
            return yaml.safe_load(f.read())


def get_hashes_of_base_lib_versions(catalog_path: str) -> dict:
    library_path = get_library_path(catalog_path)
    library_dir = pathlib.Path(library_path)
    hashes = {}
    for lib_entry in library_dir.iterdir():
        if not lib_entry.is_dir() or not RE_VERSION.match(lib_entry.name):
            continue

        hashes[lib_entry.name] = get_hash_of_directory(os.path.join(library_path, lib_entry.name), EXCLUDED_PATTERNS)

    return hashes

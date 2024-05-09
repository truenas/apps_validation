import contextlib
import yaml


def get_library_hashes(library_path: str) -> dict:
    """
    This reads from library hashes file and returns the hashes
    """
    with contextlib.suppress(FileNotFoundError, yaml.YAMLError):
        with open(library_path, 'r') as f:
            return yaml.safe_load(f.read())

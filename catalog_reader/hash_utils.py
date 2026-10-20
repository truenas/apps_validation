import shlex
import subprocess


# Never part of a library: its tests stay in the catalog and bytecode is written next to imported modules
EXCLUDED_NAMES = ('tests', '__pycache__')


def get_hash_of_directory(directory: str) -> str:
    """
    This returns sha256sum of the directory, skipping files and directories named in EXCLUDED_NAMES
    """
    names = ' -o '.join(f'-name {shlex.quote(name)}' for name in EXCLUDED_NAMES)
    cp = subprocess.run(
        f'find {shlex.quote(directory)} -mindepth 1 \\( {names} \\) -prune -o -type f -exec sha256sum {{}} + '
        '| sort | awk \'{print $1}\' | sha256sum',
        capture_output=True, check=True, shell=True,
    )
    return cp.stdout.decode().split()[0]

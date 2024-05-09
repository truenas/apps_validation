import subprocess


def get_hash_of_directory(directory: str) -> str:
    """
    This returns sha256sum of the directory
    """
    cp = subprocess.run(
        f'find {directory} -type f -exec sha256sum {{}} + | sort | sha256sum',
        capture_output=True, check=True, shell=True,
    )
    return cp.stdout.decode().split()[0]

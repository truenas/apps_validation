import subprocess


def get_hash_of_directory(directory: str, exclude_patters: list[str] | None = None) -> str:
    """
    This returns sha256sum of the directory
    """
    exclude_patters = exclude_patters or []
    find_command = f'find {directory} -type f"'
    for pattern in exclude_patters:
        find_command += f' -not -path "{directory}/**/{pattern}*"'

    find_command += ' -exec sha256sum {{}} + | sort | awk \'{{print $1}}\' | sha256sum'

    cp = subprocess.run(find_command, capture_output=True, check=True, shell=True)
    return cp.stdout.decode().split()[0]

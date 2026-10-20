import hashlib
import os


# Never part of a library: its tests stay in the catalog and bytecode is written next to imported modules
EXCLUDED_NAMES = ('tests', '__pycache__')


def get_hash_of_directory(directory: str) -> str:
    """
    This returns sha256sum of the directory, skipping files and directories named in EXCLUDED_NAMES

    Matches the `find -type f -exec sha256sum | sort | awk '{print $1}' | sha256sum` it replaces, so the
    lib_version_hash values already stored in the catalog stay valid: the sha256 of the sorted file digests,
    one per line. Symlinks and special files are skipped, like `find -type f` does.
    """
    hashes = []
    stack = [directory]
    while stack:
        with os.scandir(stack.pop()) as it:
            for entry in it:
                if entry.name in EXCLUDED_NAMES:
                    continue
                if entry.is_dir(follow_symlinks=False):
                    stack.append(entry.path)
                elif entry.is_file(follow_symlinks=False):
                    with open(entry.path, 'rb') as f:
                        hashes.append(hashlib.file_digest(f, 'sha256').hexdigest())

    digest = hashlib.sha256()
    for h in sorted(hashes):
        digest.update(f'{h}\n'.encode())
    return digest.hexdigest()

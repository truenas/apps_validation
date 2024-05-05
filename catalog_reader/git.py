import contextlib
import subprocess

from datetime import datetime
from typing import Optional


def get_last_updated_date(repo_path: str, folder_path: str) -> Optional[str]:
    with contextlib.suppress(Exception):
        # We don't want to fail querying items if for whatever reason this fails
        output = subprocess.check_output(
            ['git', 'log', '-n', '1', '--pretty=format:%ct', f'{folder_path}'],
            cwd=repo_path,
            stderr=subprocess.DEVNULL
        )
        if output:
            timestamp = datetime.fromtimestamp(int(output))
            return timestamp.strftime('%Y-%m-%d %H:%M:%S')

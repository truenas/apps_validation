import contextlib
import os.path

from apps_exceptions import ValidationErrors


def validate_k8s_to_docker_migrations(verrors: ValidationErrors, app_migration_path: str, schema: str):
    file_to_check_path = os.path.join(app_migration_path, 'migrate_from_kubernetes')
    with contextlib.suppress(FileNotFoundError):
        with open(file_to_check_path, 'r') as r:
            if not r.readline().startswith('#!'):
                verrors.add(schema, 'Migration file should start with shebang line')

        if not os.access(file_to_check_path, os.X_OK):
            verrors.add(schema, 'Migration file is not executable')

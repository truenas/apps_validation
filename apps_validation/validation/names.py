import pathlib
import re


RE_SCALE_VERSION = re.compile(r'^(\d{2}\.\d{2}(?:\.\d)*(?:-?(?:RC|BETA)\.?\d?)?)$')  # 24.04 / 24.04.1 / 24.04-RC.1
RE_TRAIN_NAME = re.compile(r'^\w+[\w.-]*$')
TEST_VALUES_DIR = 'test_values'
TEST_VALUES_FILENAME = 'test_values.yaml'


def get_test_values_from_test_dir(test_dir_path: str) -> list:
    values_dir = pathlib.Path(test_dir_path)
    if not values_dir.is_dir():
        return []

    return [entry.name for entry in values_dir.iterdir() if entry.is_file() and entry.name.endswith('.yaml')]

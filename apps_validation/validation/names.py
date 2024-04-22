import re


RE_SCALE_VERSION = re.compile(r'^(\d{2}\.\d{2}(?:\.\d)*(?:-?(?:RC|BETA)\.?\d?)?)$')  # 24.04 / 24.04.1 / 24.04-RC.1
RE_TRAIN_NAME = re.compile(r'^\w+[\w.-]*$')

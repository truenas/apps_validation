import re


RE_VERSION_PATTERN = re.compile(r'(\d{2}\.\d{2}(?:\.\d)*)')  # We are only interested in XX.XX here

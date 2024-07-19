# src/utils/general_utility.py

import re

def validate_username(username: str) -> bool:
    """Validate the format of a RuneScape username."""
    pattern = r'^[a-zA-Z0-9](([a-zA-Z0-9]| (?! )){0,10}[a-zA-Z0-9])?$'
    return bool(re.match(pattern, username))
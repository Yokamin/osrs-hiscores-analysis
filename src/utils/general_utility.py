# src/utils/general_utility.py

import re

def validate_username(username: str) -> bool:
    """Validate the format of a RuneScape username."""
    pattern = r'^[a-zA-Z0-9](([a-zA-Z0-9]| (?! )){0,10}[a-zA-Z0-9])?$'
    return bool(re.match(pattern, username))

# TODO

# function to validate group of users
# useful to run before api call as to not run pointless calls

# determine game mode
#   currently checks one user at a time
#   api file only has the exact api call
#   other script will have to work the list of users etc
#   and finally determine to put rank per game mode OR find common mode
#       should be able to find common game mode for list of usernames based on:



# data_processor
#   fix so to properly fill in data based on template from category_loader



# start comparison script
#   should be able to compare regardless of game mode (skip ranks)
#   should be able to compare game mode specific (needs determine gamemode)
#   figure out required args for this
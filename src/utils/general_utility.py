# src/utils/general_utility.py

import re
from ..api.hiscores_api import HiscoresAPI, GameMode
from .logger import console_logger
from .category_loader import CategoryLoader, Categories

def validate_usernames(usernames: list[str]) -> tuple[list[str], list[str]]:
    """
    Validate one or more Old School RuneScape usernames.

    This function checks if given usernames adhere to the OSRS username rules:
    - Can contain letters (a-z, A-Z), numbers (0-9), and spaces
    - Must be 1-12 characters long
    - Cannot start or end with a space
    - Cannot contain two consecutive spaces

    Args:
        usernames (list[str]): A list containing one or more usernames to validate.

    Returns:
        tuple[list[str], list[str]]: A tuple containing two lists:
            1. List of valid usernames
            2. List of invalid usernames

    Examples:
        >>> validate_usernames(["Zezima"])
        (['Zezima'], [])
        >>> validate_usernames(["Player 123", "Invalid  Name", "", "Zezima"])
        (['Player 123', 'Zezima'], ['Invalid  Name', ''])
    """
    pattern = r'^[a-zA-Z0-9](([a-zA-Z0-9]| (?! )){0,10}[a-zA-Z0-9])?$'
    valid_usernames = []
    invalid_usernames = []

    for username in usernames:
        if username and re.match(pattern, username):
            valid_usernames.append(username)
        else:
            invalid_usernames.append(username)

    return valid_usernames, invalid_usernames

def check_missing_categories(username: str) -> tuple[list[str], list[str]]:
    """
    Check for any missing categories in the local category list compared to the API data.

    This function fetches data for the specified username from the API and compares it
    with the local list of all skills and activities to identify any missing categories.

    Args:
        username (str): The name of the username to fetch data for.

    Returns:
        tuple[list[str], list[str]]: A tuple containing two lists:
            1. List of missing skills
            2. List of missing activities

    Raises:
        ValueError: If the username data cannot be fetched from the API.

    Example:
        >>> missing_skills, missing_activities = check_missing_categories("Zezima")
        >>> print(f"Missing skills: {missing_skills}")
        >>> print(f"Missing activities: {missing_activities}")
    """
    console_logger.info("Initiating category comparison")
    
    api = HiscoresAPI()
    player_data = api.get_player_data_from_api(username, GameMode.REGULAR)

    if not player_data:
        console_logger.error("Failed to fetch API data")
        raise ValueError("Unable to fetch API data for comparison")

    # Get all local categories
    console_logger.info("Loading local category data")
    local_skills = set(CategoryLoader.get_category(Categories.ALL_SKILLS))
    local_activities = set(CategoryLoader.get_category(Categories.ALL_ACTIVITIES))

    # Extract categories from API data
    console_logger.info("Extracting categories from API data")
    api_skills = {skill['name'] for skill in player_data['skills']}
    api_activities = {activity['name'] for activity in player_data['activities']}

    # Find missing categories
    console_logger.info("Comparing local categories with API categories")
    missing_skills = api_skills - local_skills
    missing_activities = api_activities - local_activities

    if missing_skills:
        console_logger.warning(f"Found {len(missing_skills)} missing skills in local data")
        console_logger.info(f"Missing skills: {', '.join(missing_skills)}")
    if missing_activities:
        console_logger.warning(f"Found {len(missing_activities)} missing activities in local data")
        console_logger.info(f"Missing activities: {', '.join(missing_activities)}")
    if not missing_skills and not missing_activities:
        console_logger.info("Local category data is up-to-date. No missing categories found")

    console_logger.info("Category comparison completed")
    return list(missing_skills), list(missing_activities)
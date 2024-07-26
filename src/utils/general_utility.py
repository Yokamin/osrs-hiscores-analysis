# src/utils/general_utility.py

import re
from ..api.hiscores_api import HiscoresAPI, GameMode
from .logger import console_logger, logger
from .category_loader import CategoryLoader, CategoryGroups
from dataclasses import dataclass

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
    if not usernames:
        raise ValueError("The list of usernames to validate cannot be empty.")
    
    pattern = r'^[a-zA-Z0-9](([a-zA-Z0-9]| (?! )){0,10}[a-zA-Z0-9])?$'
    valid_usernames = []
    invalid_usernames = []

    for username in usernames:
        if username and re.match(pattern, username):
            valid_usernames.append(username)
        else:
            invalid_usernames.append(username)

    return valid_usernames, invalid_usernames

@dataclass
class CategoryComparison:
    missing_skills: list[str]
    missing_activities: list[str]
    extra_skills: list[str]
    extra_activities: list[str]

def check_missing_categories(username: str) -> CategoryComparison | None:
    """
    Check for any discrepancies between the local category list and the API data.

    This function fetches data for the specified username from the API and compares it
    with the local list of all skills and activities to identify any missing or extra categories.

    Args:
        username (str): The name of the username to fetch data for.

    Returns:
        CategoryComparison | None: An object containing lists of missing and extra skills and activities,
                                   or None if there are no discrepancies.

    Raises:
        ValueError: If the username data cannot be fetched from the API.

    Example:
        >>> result = check_missing_categories("Zezima")
        >>> if result:
        ...     print(f"Missing skills: {result.missing_skills}")
        ...     print(f"Extra activities: {result.extra_activities}")
        ... else:
        ...     print("No discrepancies found")
    """
    console_logger.info("Initiating category comparison")
    
    api = HiscoresAPI()
    player_data = api.get_player_data_from_api(username, GameMode.REGULAR)

    if not player_data:
        console_logger.error("Failed to fetch API data")
        raise ValueError("Unable to fetch API data for comparison")

    # Get all local categories
    logger.info("Loading local category data")
    try:
        categories = CategoryLoader.get_categories([CategoryGroups.ALL_SKILLS, CategoryGroups.ALL_ACTIVITIES])
        local_skills = set(categories[CategoryGroups.ALL_SKILLS.value])
        local_activities = set(categories[CategoryGroups.ALL_ACTIVITIES.value])
    except Exception as e:
        console_logger.error(f"Error loading local categories: {e}")
        raise ValueError("Unable to load local categories for comparison")

    # Extract categories from API data
    logger.info("Extracting categories from API data")
    api_skills = {skill['name'] for skill in player_data['skills']}
    api_activities = {activity['name'] for activity in player_data['activities']}

    # Find missing and extra categories
    logger.info("Comparing local categories with API categories")
    missing_skills = api_skills - local_skills
    missing_activities = api_activities - local_activities
    extra_skills = local_skills - api_skills
    extra_activities = local_activities - api_activities

    # Check if there are any discrepancies
    if not any([missing_skills, missing_activities, extra_skills, extra_activities]):
        console_logger.info("Local category data matches API data. No discrepancies found")
        logger.info("Category comparison completed")
        return None

    result = CategoryComparison(
        list(missing_skills),
        list(missing_activities),
        list(extra_skills),
        list(extra_activities)
    )

    # Log results
    for attr, desc in [
        ('missing_skills', 'missing skills in local data'),
        ('missing_activities', 'missing activities in local data'),
        ('extra_skills', 'extra skills in local data'),
        ('extra_activities', 'extra activities in local data')
    ]:
        items = getattr(result, attr)
        if items:
            console_logger.warning(f"Found {len(items)} {desc}")
            console_logger.info(f"{attr.capitalize()}: {', '.join(items)}")

    logger.info("Category comparison completed")

    return result
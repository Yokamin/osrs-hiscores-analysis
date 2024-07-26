# main.py

import json

from src.utils.category_loader import CategoryLoader, CategoryGroups
from src.utils.data_processor import process_multiple_players
from src.api.hiscores_api import HiscoresAPI, GameMode
from src.utils.general_utility import check_missing_categories, validate_usernames
from src.utils.logger import logger, console_logger, get_module_logger

# Setup module-specific logger
module_logger = get_module_logger(__name__)

def main():
    """
    Main function to demonstrate the usage of OSRS Hiscores Analysis tools.

    This function performs the following steps:
    1. Validates usernames
    2. Checks for missing category data
    3. Loads categories
    4. Fetches player data from the API
    5. Processes the player data
    6. Logs the results
    """

    # Usernames
    test_users: list[str] = ["Lynx Titan", "Zezima"]

    # Gamemode
    game_mode: GameMode = GameMode.REGULAR

    # Categories
    categories: list[CategoryGroups] = [CategoryGroups.COMBAT, CategoryGroups.RAIDS]

    # Validate usernames
    valid_usernames, invalid_usernames = validate_usernames(test_users)
    if invalid_usernames:
        console_logger.warning(f"Invalid usernames found: {invalid_usernames}")
        console_logger.info(f"Valid usernames: {valid_usernames}")
    elif not valid_usernames:
        console_logger.error("No valid usernames found. Please check your config.")
        return

    # Check for missing category data
    try:
        missing_category_data = check_missing_categories(valid_usernames[0])
        if missing_category_data:
            console_logger.warning("Found discrepancies:")
            for key, value in missing_category_data.__dict__.items():
                if value:
                    console_logger.warning(f"{key}: {value}")
            return
    except Exception as e:
        console_logger.error(f"Error checking missing categories: {e}")
        logger.exception("Detailed error when checking missing categories:")
        return

    # Load categories
    try:
        loaded_categories: dict[str, list[str] | None] = CategoryLoader.get_categories(categories)
        if not loaded_categories:
            console_logger.error("Failed to load categories. Please check your configuration.")
            return
    except Exception as e:
        console_logger.error(f"Error loading categories: {e}")
        logger.exception("Detailed error when loading categories:")
        return

    # Get player data from API
    try:
        raw_player_data = HiscoresAPI.get_multiple_player_data(valid_usernames, game_mode)
        if not raw_player_data:
            console_logger.error("Failed to fetch player data from API.")
            return
    except Exception as e:
        console_logger.error(f"Error fetching player data: {e}")
        logger.exception("Detailed error when fetching player data:")
        return

    # Process skillg and Activities using loaded categories
    try:
        processed_players, unprocessed_players = process_multiple_players(raw_player_data, loaded_categories)
        if not processed_players:
            console_logger.error("Failed to process player data.")
            return
    except Exception as e:
        console_logger.error(f"Error processing player data: {e}")
        logger.exception("Detailed error when processing player data:")
        return

    # Log results
    console_logger.info("Processed Players Data:")
    console_logger.info(json.dumps(processed_players, indent=4))
    if unprocessed_players:
        console_logger.warning("Unprocessed Players:")
        console_logger.warning(json.dumps(unprocessed_players, indent=4))

if __name__ == "__main__":
    main()

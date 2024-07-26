# src\utils\data_processor.py

from ..api.hiscores_api import PlayerData
from ..utils.logger import console_logger, logger

def process_data(api_data: PlayerData, categories: dict[str, list[str]]) -> dict[str, dict[str, int | str | None]] | None:
    """
    Process player data from the OSRS Hiscores API.

    This function takes raw API data for a player and processes it
    according to the specified categories. It extracts relevant skill and
    activity data based on the provided categories.

    Args:
        api_data (PlayerData): Object containing raw API data.
        categories (dict[str, list[str]]): A dictionary where keys are category group names
                                           and values are lists of category names to process.

    Returns:
        dict[str, dict[str, int | str | None]] | None: A dictionary containing processed data for each category,
                                                      or None if processing fails.
        The structure is:
        {
            'game_mode': str,
            'category_name': {
                'rank': int,
                'level': int,
                'xp': int
            } | {
                'rank': int,
                'score': int
            }
        }

    Raises:
        KeyError: If the expected data structure is not present in the API data.

    Note:
        The function logs errors for missing categories and any exceptions during processing.
    """
    if not categories:
        console_logger.error("No categories provided for processing")
        return None
    
    logger.info(f"Starting to process data for {sum(len(cat) for cat in categories)} categories")
    try:
        processed_data: dict[str, dict[str, int | str | None]] = {
            "game_mode": api_data.get("game_mode"),
        }

        # Create dictionaries for faster lookup
        skills_dict = {s["name"]: s for s in api_data.get("skills", [])}
        activities_dict = {a["name"]: a for a in api_data.get("activities", [])}

        missing_categories = []

        for category_group, category_items in categories.items():
            for category in category_items:
                if category in skills_dict:
                    skill_data = skills_dict[category]
                    processed_data[category] = {
                        "rank": skill_data["rank"],
                        "level": skill_data["level"],
                        "xp": skill_data["xp"]
                    }
                elif category in activities_dict:
                    activity_data = activities_dict[category]
                    processed_data[category] = {
                        "rank": activity_data["rank"],
                        "score": activity_data["score"]
                    }
                else:
                    missing_categories.append(category)

        if missing_categories:
            error_message = f"Categories not found in API data: {', '.join(missing_categories)}"
            console_logger.error(error_message)
            return None

        logger.info(f"Processed data for {len(processed_data) - 1} categories")  # -1 for 'game_mode'
        return processed_data

    except Exception as e:
        console_logger.error(f"Error processing data: {str(e)}")
        return None

def process_multiple_players(players_data: dict[str, PlayerData], categories: dict[str, list[str]]) -> tuple[dict[str, dict[str, dict[str, int | str | None]]], list[str]] | None:
    """
    Process data for multiple players from the OSRS Hiscores API.

    This function iterates through the provided player data, processing each player's
    data according to the specified categories.

    Args:
        players_data (dict[str, PlayerData]): A dictionary where keys are player names
                                              and values are PlayerData objects.
        categories (dict[str, list[str]]): A dictionary where keys are category group names
                                           and values are lists of category names to process.

    Returns:
        tuple[dict[str, dict[str, dict[str, int | str | None]]], list[str]] | None: 
            A tuple containing:
            1. A dictionary of processed player data, where keys are player names and values are processed data.
            2. A list of player names for which processing failed.
            Returns None if no players could be processed at all.

    The structure of the processed data dictionary is:
    {
        'player_name': {
            'game_mode': str,
            'category_name': {
                'rank': int,
                'level': int,
                'xp': int
            } | {
                'rank': int,
                'score': int
            }
        }
    }

    Note:
        - The function logs information about the number of players and categories being processed.
        - It also logs warnings for players whose data could not be processed.
        - If no players could be processed, it logs an error and returns None.
    """
    if not players_data or not categories:
        console_logger.error("No player data or categories provided for processing")
        return None

    console_logger.info(f"Starting to process data for {len(players_data)} players and {sum(len(cat) for cat in categories.values())} categories")
    processed_players = {}
    unprocessed_players = []

    for player_name, player_data in players_data.items():
        processed_player_data = process_data(player_data, categories)
        if processed_player_data:
            processed_players[player_name] = processed_player_data
        else:
            console_logger.warning(f"Failed to process data for player: {player_name}")
            unprocessed_players.append(player_name)

    if not processed_players:
        console_logger.error("Failed to process data for any players")
        return None

    console_logger.info(f"Successfully processed data for {len(processed_players)} players and {sum(len(cat) for cat in categories.values())} categories")
    if unprocessed_players:
        console_logger.warning(f"Failed to process data for {len(unprocessed_players)} players: {', '.join(unprocessed_players)}")

    return processed_players, unprocessed_players
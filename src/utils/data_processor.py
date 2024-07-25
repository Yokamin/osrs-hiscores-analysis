# src\utils\data_processor.py

from ..api.hiscores_api import PlayerData
from ..utils.logger import console_logger

def process_data(api_data: PlayerData, categories: list[str]) -> dict[str, dict[str, int | str | None]] | None:
    """
    Process player data from the OSRS Hiscores API.

    This function takes raw API data for a player and processes it
    according to the specified categories. It extracts relevant skill and
    activity data based on the provided categories.

    Args:
        api_data: PlayerData object containing raw API data.
        categories: A list of category names (skills or activities) to process.

    Returns:
        A dictionary containing processed data for each category, or None if processing fails.
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
    """
    console_logger.info(f"Starting to process data for {len(categories)} categories")
    try:
        processed_data: dict[str, dict[str, int | str | None]] = {
            "game_mode": api_data.get("game_mode"),
        }

        # Create dictionaries for faster lookup
        skills_dict = {s["name"]: s for s in api_data.get("skills", [])}
        activities_dict = {a["name"]: a for a in api_data.get("activities", [])}

        missing_categories = []

        for category in categories:
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

        console_logger.info(f"Processed data for {len(categories)} categories")
        return processed_data

    except Exception as e:
        console_logger.error(f"Error processing data: {str(e)}")
        return None
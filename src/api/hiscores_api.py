# src/api/hiscores_api.py

from enum import Enum
import requests
from ..utils.logger import logger, console_logger
from urllib.parse import quote
from typing import TypedDict

class GameMode(Enum):
    """Enum representing different game modes in Old School RuneScape."""
    REGULAR = "regular"
    IRONMAN = "ironman"
    HARDCORE = "hardcore"
    ULTIMATE = "ultimate"

class PlayerData[T: str | int](TypedDict):
    """TypedDict representing the structure of player data."""
    game_mode: str
    skills: list[dict[str, T]]
    activities: list[dict[str, T]]

class HiscoresAPI:
    """
    A class for interacting with the Old School RuneScape Hiscores API.

    This class provides methods to fetch and process hiscore data for OSRS players.
    """

    BASE_URLS = {
        GameMode.REGULAR: "https://secure.runescape.com/m=hiscore_oldschool/index_lite.json?player=",
        GameMode.IRONMAN: "https://secure.runescape.com/m=hiscore_oldschool_ironman/index_lite.json?player=",
        GameMode.HARDCORE: "https://secure.runescape.com/m=hiscore_oldschool_hardcore_ironman/index_lite.json?player=",
        GameMode.ULTIMATE: "https://secure.runescape.com/m=hiscore_oldschool_ultimate/index_lite.json?player="
    }

    @staticmethod
    def _make_api_call(url: str, username: str) -> requests.Response:
        """
        Make an API call and return the raw response.

        Args:
            url (str): The base URL for the API call.
            username (str): The username to query.

        Returns:
            requests.Response: The raw response from the API.

        Raises:
            requests.RequestException: If there's an error with the API request.
        """
        logger.info(f"Making API call for player '{username}'...")
        response = requests.get(f"{url}{quote(username)}", timeout=10)
        response.raise_for_status()
        return response

    @staticmethod
    def _parse_api_response(response: requests.Response, game_mode: GameMode) -> PlayerData:
        """
        Parse the API response into PlayerData structure.

        Args:
            response (requests.Response): The raw API response.
            game_mode (GameMode): The game mode of the player.

        Returns:
            PlayerData: The parsed player data.

        Raises:
            KeyError: If the expected data is not present in the response.
        """
        logger.info(f"Parsing API response for {game_mode.value} mode...")
        data: dict = response.json()
        return PlayerData(
            game_mode=game_mode.name,
            skills=data['skills'],
            activities=data['activities']
        )

    @classmethod
    def get_player_data_from_api(cls, username: str, game_mode: GameMode) -> PlayerData | None:
        """
        Fetch player data from the OSRS Hiscores API.

        Args:
            username (str): The player's username.
            game_mode (GameMode): The game mode to fetch data for.

        Returns:
            PlayerData | None: The player's data if found, None otherwise.
        """
        logger.info(f"Fetching data for player '{username}' in {game_mode.value} mode...")
        url = cls.BASE_URLS.get(game_mode)
        if not url:
            console_logger.error(f"Invalid game mode: {game_mode.value}")
            return None

        try:
            response = cls._make_api_call(url, username)
            return cls._parse_api_response(response, game_mode)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                logger.info(f"No data found for username '{username}' in game mode '{game_mode.value}'.")
            else:
                console_logger.error(f"HTTP error fetching data for '{username}' in {game_mode.value}: {e}")
            return None
        except requests.RequestException as e:
            console_logger.error(f"Request error fetching data for {username} in {game_mode.value} mode: {e}")
            return None
        except KeyError as e:
            console_logger.error(f"Error parsing data for {username} in {game_mode.value} mode: {e}")
            return None

    @classmethod
    def get_multiple_player_data(cls, usernames: list[str], game_mode: GameMode = GameMode.REGULAR) -> dict[str, PlayerData]:
        """
        Fetch player data for multiple usernames from the OSRS Hiscores API.

        Args:
            usernames (List[str]): A list of player usernames to fetch data for.
            game_mode (GameMode, optional): The game mode to fetch data for. Defaults to GameMode.REGULAR.

        Returns:
            Dict[str, PlayerData]: A dictionary where keys are usernames and values are PlayerData objects.
                                   Usernames for which data couldn't be fetched are omitted from the result.
        """
        console_logger.info(f"Fetching data for {len(usernames)} players in {game_mode.value} mode...")
        player_data = {}
        for username in usernames:
            data = cls.get_player_data_from_api(username, game_mode)
            if data:
                player_data[username] = data
            else:
                console_logger.warning(f"Could not fetch data for player '{username}'")
        
        console_logger.info(f"Successfully fetched data for {len(player_data)} out of {len(usernames)} players")
        return player_data

    @classmethod
    def determine_game_mode(cls, username: str, skip_hardcore: bool = False, skip_uim: bool = False) -> GameMode | None:
        """
        Determine the game mode of a player.

        Args:
            username (str): The player's username.
            skip_hardcore (bool, optional): Whether to skip checking for Hardcore Ironman mode. Defaults to False.
            skip_uim (bool, optional): Whether to skip checking for Ultimate Ironman mode. Defaults to False.

        Returns:
            GameMode | None: The determined game mode, or None if unable to determine.
        """
        console_logger.info(f"Determining game mode for player '{username}'...")
        modes_to_check = [GameMode.IRONMAN, GameMode.REGULAR]
        if not skip_hardcore:
            modes_to_check.insert(0, GameMode.HARDCORE)
        if not skip_uim:
            modes_to_check.insert(0, GameMode.ULTIMATE)

        for mode in modes_to_check:
            if cls.get_player_data_from_api(username, mode) is not None:
                console_logger.info(f'Game mode found for "{username}": {mode.value}')
                return mode

        console_logger.warning(f'Unable to determine game mode for "{username}". Account may not exist.')
        return None


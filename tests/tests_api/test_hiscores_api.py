# tests/tests_api/test_hiscores_api.py

import pytest
import json
import os
import requests
from src.api.hiscores_api import HiscoresAPI, GameMode

# Load the expected skills and activities data from the JSON file
EXPECTED_DATA_FILE = os.path.join(os.path.dirname(__file__), 'expected_skills_and_activities.json')
with open(EXPECTED_DATA_FILE, 'r') as f:
    EXPECTED_DATA = json.load(f)

def test_base_urls():
    """Test the base URLs for the Hiscores API."""
    assert HiscoresAPI.BASE_URLS == {
        GameMode.REGULAR: "https://secure.runescape.com/m=hiscore_oldschool/index_lite.json?player=",
        GameMode.IRONMAN: "https://secure.runescape.com/m=hiscore_oldschool_ironman/index_lite.json?player=",
        GameMode.HARDCORE: "https://secure.runescape.com/m=hiscore_oldschool_hardcore_ironman/index_lite.json?player=",
        GameMode.ULTIMATE: "https://secure.runescape.com/m=hiscore_oldschool_ultimate/index_lite.json?player="
    }

def test_make_api_call(regular_username):
    """
    Test the _make_api_call method using the live API endpoint.

    Args:
        regular_username (str): The username to use for the test.
    """
    url = HiscoresAPI.BASE_URLS[GameMode.REGULAR]
    response = HiscoresAPI._make_api_call(url, regular_username)
    assert isinstance(response, requests.Response)
    assert response.status_code == 200

def test_parse_api_response(regular_username):
    """
    Test the _parse_api_response method using the live API response.

    Args:
        regular_username (str): The username to use for the test.
    """
    game_mode = GameMode.REGULAR
    url = HiscoresAPI.BASE_URLS[game_mode]
    response = HiscoresAPI._make_api_call(url, regular_username)
    result = HiscoresAPI._parse_api_response(response, game_mode)

    # Check that 'game_mode' exists, is a string and is equal to the game mode name
    assert 'game_mode' in result
    assert isinstance(result['game_mode'], str)
    assert result['game_mode'] == game_mode.name
    # Check that 'skills' and 'activities' exist and are lists
    assert 'skills' in result
    assert isinstance(result['skills'], list)
    assert 'activities' in result
    assert isinstance(result['activities'], list)

def test_determine_game_mode(all_game_modes_usernames):
    """
    Test the determine_game_mode method.

    Args:
        all_game_modes_usernames (dict[str, str]): A dictionary mapping game mode names to usernames.
    """
    for game_mode, username in all_game_modes_usernames.items():
        result = HiscoresAPI.determine_game_mode(username)
        assert result == GameMode[game_mode.upper()]

        # Test with skip_hardcore=True
        if game_mode == "hardcore":
            result = HiscoresAPI.determine_game_mode(username, skip_hardcore=True)
            assert result == GameMode.IRONMAN

        # Test with skip_uim=True
        if game_mode == "ultimate":
            result = HiscoresAPI.determine_game_mode(username, skip_uim=True)
            assert result == GameMode.IRONMAN

def test_get_player_data_from_api(regular_username):
    """
    Test the get_player_data_from_api method.

    Args:
        regular_username (str): The username to use for the test.
    """
    result = HiscoresAPI.get_player_data_from_api(regular_username, GameMode.REGULAR)
    assert result is not None
    assert result['game_mode'] == GameMode.REGULAR.name
    assert all(skill in EXPECTED_DATA['skills'] for skill in [s['name'] for s in result['skills']])
    assert len(result['skills']) >= len(EXPECTED_DATA['skills'])
    assert all(activity in EXPECTED_DATA['activities'] for activity in [a['name'] for a in result['activities']])
    assert len(result['activities']) >= len(EXPECTED_DATA['activities'])

def test_get_player_data_all_game_modes(all_game_modes_usernames):
    """
    Test the get_player_data_from_api method for all game modes.

    Args:
        all_game_modes_usernames (dict[str, str]): A dictionary mapping game mode names to usernames.
    """
    for game_mode, username in all_game_modes_usernames.items():
        result = HiscoresAPI.get_player_data_from_api(username, GameMode[game_mode.upper()])
        assert result is not None
        assert result['game_mode'] == GameMode[game_mode.upper()].name

def test_username_incorrect_game_mode(regular_username):
    """
    Test the get_player_data_from_api method when the game mode doesn't exist for the given username.

    Args:
        regular_username (str): The username to use for the test.
    """
    for game_mode in [GameMode.HARDCORE, GameMode.ULTIMATE, GameMode.IRONMAN]:
        if game_mode.value != regular_username:
            result = HiscoresAPI.get_player_data_from_api(regular_username, game_mode)
            assert result is None

def test_invalid_game_mode(regular_username):
    """
    Test the get_player_data_from_api method with an invalid game mode.

    Args:
        regular_username (str): The username to use for the test.
    """
    with pytest.raises(ValueError):
        invalid_game_mode = GameMode("INVALID_MODE")
        result = HiscoresAPI.get_player_data_from_api(regular_username, invalid_game_mode)
        assert result is None

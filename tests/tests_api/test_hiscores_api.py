# tests/tests_api/test_hiscores_api.py

import pytest
import json
import os
import requests
from src.api.hiscores_api import HiscoresAPI, GameMode
from unittest.mock import patch, MagicMock

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

    assert 'game_mode' in result
    assert isinstance(result['game_mode'], str)
    assert result['game_mode'] == game_mode.name
    assert 'skills' in result
    assert isinstance(result['skills'], list)
    assert 'activities' in result
    assert isinstance(result['activities'], list)

def test_determine_game_mode(all_game_modes_usernames):
    """
    Test the determine_game_mode method for all game modes.

    Args:
        all_game_modes_usernames (dict[str, str]): A dictionary mapping game mode names to usernames.
    """
    for game_mode, username in all_game_modes_usernames.items():
        result = HiscoresAPI.determine_game_mode(username)
        assert result == GameMode[game_mode.upper()]

        if game_mode == "hardcore":
            result = HiscoresAPI.determine_game_mode(username, skip_hardcore=True)
            assert result == GameMode.IRONMAN

        if game_mode == "ultimate":
            result = HiscoresAPI.determine_game_mode(username, skip_uim=True)
            assert result == GameMode.IRONMAN

def test_get_player_data_from_api(regular_username):
    """
    Test the get_player_data_from_api method for a regular player.

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

def test_get_multiple_player_data(all_game_modes_usernames):
    """
    Test the get_multiple_player_data method with valid and invalid usernames.

    Args:
        all_game_modes_usernames (dict[str, str]): A dictionary mapping game mode names to usernames.
    """
    usernames = list(all_game_modes_usernames.values())[:2]
    result = HiscoresAPI.get_multiple_player_data(usernames, GameMode.REGULAR)
    
    assert isinstance(result, dict)
    assert len(result) <= len(usernames)
    
    for username, data in result.items():
        assert username in usernames
        assert isinstance(data, dict)
        assert 'game_mode' in data
        assert data['game_mode'] == GameMode.REGULAR.name
        assert 'skills' in data
        assert isinstance(data['skills'], list)
        assert 'activities' in data
        assert isinstance(data['activities'], list)

    invalid_usernames = usernames + ['ThisUsernameDoesNotExist12345']
    result_with_invalid = HiscoresAPI.get_multiple_player_data(invalid_usernames, GameMode.REGULAR)
    assert len(result_with_invalid) < len(invalid_usernames)
    assert 'ThisUsernameDoesNotExist12345' not in result_with_invalid

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
    Test get_player_data_from_api with incorrect game modes for a regular username.

    Args:
        regular_username (str): The username to use for the test.
    """
    for game_mode in [GameMode.HARDCORE, GameMode.ULTIMATE, GameMode.IRONMAN]:
        if game_mode.value != regular_username:
            result = HiscoresAPI.get_player_data_from_api(regular_username, game_mode)
            assert result is None

def test_invalid_game_mode(regular_username):
    """
    Test get_player_data_from_api with an invalid game mode.

    Args:
        regular_username (str): The username to use for the test.
    """
    with pytest.raises(ValueError):
        invalid_game_mode = GameMode("INVALID_MODE")
        result = HiscoresAPI.get_player_data_from_api(regular_username, invalid_game_mode)
        assert result is None

def test_get_multiple_player_data_empty_list():
    """Test get_multiple_player_data with an empty list of usernames."""
    result = HiscoresAPI.get_multiple_player_data([])
    assert result == {}

@patch.object(HiscoresAPI, 'get_player_data_from_api')
def test_determine_game_mode_none(mock_get_player_data):
    """Test determine_game_mode when it can't determine the game mode."""
    mock_get_player_data.return_value = None
    result = HiscoresAPI.determine_game_mode("NonexistentUser")
    assert result is None

    assert mock_get_player_data.call_count == 4  # ULTIMATE, HARDCORE, IRONMAN, REGULAR
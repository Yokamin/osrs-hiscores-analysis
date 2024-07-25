# tests/tests_utils/test_general_utility.py

import pytest
from unittest.mock import patch
from src.utils.general_utility import validate_usernames, check_missing_categories
from src.api.hiscores_api import HiscoresAPI
from src.utils.category_loader import Categories

def test_validate_usernames():
    valid, invalid = validate_usernames(["Zezima", "Player 123", "Invalid  Name", "", "TooLongUsername123"])
    assert valid == ["Zezima", "Player 123"]
    assert invalid == ["Invalid  Name", "", "TooLongUsername123"]

def test_validate_usernames_empty_list():
    with pytest.raises(ValueError, match="The list of usernames to validate cannot be empty."):
        validate_usernames([])

def test_validate_usernames_all_valid():
    valid, invalid = validate_usernames(["Zezima", "Player123", "Hello World"])
    assert valid == ["Zezima", "Player123", "Hello World"]
    assert invalid == []

def test_validate_usernames_all_invalid():
    valid, invalid = validate_usernames(["", "Invalid  Name", "TooLongUsername123"])
    assert valid == []
    assert invalid == ["", "Invalid  Name", "TooLongUsername123"]

def test_validate_usernames_edge_cases():
    valid, invalid = validate_usernames([
        "Normal123",
        "With Space",
        "12CharName12",  # Valid (12 characters)
        "13CharName123", # Invalid (13 characters)
        " SpaceStart",
        "SpaceEnd ",
        "Double  Space",
        "Symbol@User",
        "Émile",  # Non-ASCII character
        "أحمد",  # Non-Latin script
        "\t",  # Tab character
        "\n",  # Newline character
        "a" * 12,  # Valid (12 characters)
        "a" * 13,  # Invalid (13 characters)
    ])
    
    assert valid == ["Normal123", "With Space", "12CharName12", "a" * 12]
    assert invalid == [
        "13CharName123",
        " SpaceStart",
        "SpaceEnd ",
        "Double  Space",
        "Symbol@User",
        "Émile",
        "أحمد",
        "\t",
        "\n",
        "a" * 13,
    ]

def test_validate_usernames_single_character():
    valid, invalid = validate_usernames(["a", "1", " ", "A"])
    assert valid == ["a", "1", "A"]
    assert invalid == [" "]

def test_validate_usernames_only_spaces():
    valid, invalid = validate_usernames(["   "])
    assert valid == []
    assert invalid == ["   "]

@pytest.fixture
def mock_api_data():
    return {
        'game_mode': 'REGULAR',
        'skills': [
            {'name': 'Attack', 'rank': 100, 'level': 99, 'xp': 13034431},
            {'name': 'NewSkill', 'rank': 1, 'level': 120, 'xp': 200000000}
        ],
        'activities': [
            {'name': 'Bounty Hunter', 'rank': 1, 'score': 1000},
            {'name': 'NewActivity', 'rank': 1, 'score': 5000}
        ]
    }

@pytest.fixture
def mock_category_data():
    return {
        Categories.ALL_SKILLS: ['Attack', 'Strength', 'Defence'],
        Categories.ALL_ACTIVITIES: ['Bounty Hunter', 'Clue Scrolls']
    }

@patch.object(HiscoresAPI, 'get_player_data_from_api')
@patch('src.utils.general_utility.CategoryLoader.get_category')
def test_check_missing_categories(mock_get_category, mock_get_player_data, mock_api_data, mock_category_data):
    mock_get_player_data.return_value = mock_api_data
    mock_get_category.side_effect = lambda x: mock_category_data[x]

    result = check_missing_categories("TestUser")

    assert result.missing_skills == ['NewSkill']
    assert result.missing_activities == ['NewActivity']
    assert set(result.extra_skills) == set(['Strength', 'Defence'])
    assert result.extra_activities == ['Clue Scrolls']

@patch.object(HiscoresAPI, 'get_player_data_from_api')
def test_check_missing_categories_api_failure(mock_get_player_data):
    mock_get_player_data.return_value = None

    with pytest.raises(ValueError, match="Unable to fetch API data for comparison"):
        check_missing_categories("TestUser")

@patch.object(HiscoresAPI, 'get_player_data_from_api')
@patch('src.utils.general_utility.CategoryLoader.get_category')
def test_check_missing_categories_no_missing(mock_get_category, mock_get_player_data, mock_api_data, mock_category_data):
    mock_api_data['skills'] = [{'name': 'Attack', 'rank': 100, 'level': 99, 'xp': 13034431}]
    mock_api_data['activities'] = [{'name': 'Bounty Hunter', 'rank': 1, 'score': 1000}]
    mock_get_player_data.return_value = mock_api_data
    mock_get_category.side_effect = lambda x: mock_category_data[x]

    result = check_missing_categories("TestUser")

    assert result.missing_skills == []
    assert result.missing_activities == []
    assert set(result.extra_skills) == set(['Strength', 'Defence'])
    assert result.extra_activities == ['Clue Scrolls']

@patch.object(HiscoresAPI, 'get_player_data_from_api')
@patch('src.utils.general_utility.CategoryLoader.get_category')
def test_check_missing_categories_no_discrepancies(mock_get_category, mock_get_player_data, mock_api_data, mock_category_data):
    mock_api_data['skills'] = [{'name': 'Attack', 'rank': 100, 'level': 99, 'xp': 13034431}]
    mock_api_data['activities'] = [{'name': 'Bounty Hunter', 'rank': 1, 'score': 1000}]
    mock_get_player_data.return_value = mock_api_data
    mock_category_data = {
        Categories.ALL_SKILLS: ['Attack'],
        Categories.ALL_ACTIVITIES: ['Bounty Hunter']
    }
    mock_get_category.side_effect = lambda x: mock_category_data[x]

    result = check_missing_categories("TestUser")

    assert result.missing_skills == []
    assert result.missing_activities == []
    assert result.extra_skills == []
    assert result.extra_activities == []
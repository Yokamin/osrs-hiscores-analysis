# tests/conftest.py

import pytest

@pytest.fixture
def regular_username(): # "regular" game mode
    return "Lynx Titan"

@pytest.fixture
def regular_username_multiple(): # multiple "regular" game mode users
    return ["Lynx Titan","Hey Jase", "Zezima", "B0aty"]

@pytest.fixture
def all_game_modes_usernames(): # all game modes, specific to each name
    return {
        "regular": "Lynx Titan",
        "ironman": "Iron Hyger",
        "hardcore": "5th hcim LUL",
        "ultimate": "Gibbed"
    }
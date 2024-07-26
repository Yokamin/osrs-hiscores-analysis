# tests/tests_utils/test_data_processor.py

import pytest
from unittest.mock import patch
from src.utils.data_processor import process_data

@pytest.fixture
def mock_api_data():
    return {
        'game_mode': 'REGULAR',
        'skills': [
            {'name': 'Attack', 'rank': 100, 'level': 99, 'xp': 13034431},
            {'name': 'Strength', 'rank': 200, 'level': 99, 'xp': 13034431},
        ],
        'activities': [
            {'name': 'Bounty Hunter', 'rank': 1000, 'score': 500},
            {'name': 'Clue Scrolls (all)', 'rank': 2000, 'score': 100},
        ]
    }

def test_process_data_successful(mock_api_data):
    categories = {'Test Group': ['Attack', 'Bounty Hunter']}
    result = process_data(mock_api_data, categories)

    assert result is not None
    assert result['game_mode'] == 'REGULAR'
    assert result['Attack'] == {'rank': 100, 'level': 99, 'xp': 13034431}
    assert result['Bounty Hunter'] == {'rank': 1000, 'score': 500}

def test_process_data_missing_category(mock_api_data):
    categories = {'Test Group': ['Attack', 'NonExistentCategory']}
    result = process_data(mock_api_data, categories)

    assert result is None

def test_process_data_empty_categories(mock_api_data):
    result = process_data(mock_api_data, {})

    assert result is None

def test_process_data_all_categories(mock_api_data):
    categories = {'Test Group': ['Attack', 'Strength', 'Bounty Hunter', 'Clue Scrolls (all)']}
    result = process_data(mock_api_data, categories)

    assert result is not None
    assert len(result) == 5  # game_mode + 4 categories

def test_process_data_invalid_api_data():
    invalid_data = {'game_mode': 'REGULAR'}  # Missing skills and activities
    result = process_data(invalid_data, ['Attack'])

    assert result is None

def test_process_data_exception_handling():
    def raise_exception(key):
        raise Exception("Test exception")

    invalid_data = {'get': raise_exception}
    result = process_data(invalid_data, {'Test Group': ['Attack']})

    assert result is None
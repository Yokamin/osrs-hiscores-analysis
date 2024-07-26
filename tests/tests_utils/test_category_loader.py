# test_category_loader.py

import pytest
from unittest.mock import patch, mock_open
from src.utils.category_loader import CategoryLoader, CategoryGroups

MOCK_YAML_DATA = '''
All Skills:
  - Attack
  - Strength
  - Defence
All Activities:
  - Bounty Hunter
  - Clue Scrolls
Combat:
  - Attack
  - Strength
'''

@pytest.fixture(autouse=True)
def reset_categories():
    CategoryLoader._categories = None

@pytest.fixture
def mock_yaml_file():
    with patch('builtins.open', new_callable=mock_open, read_data=MOCK_YAML_DATA):
        yield

def test_load_categories_successful(mock_yaml_file):
    CategoryLoader._load_categories()
    assert CategoryLoader._categories is not None
    assert 'All Skills' in CategoryLoader._categories
    assert 'All Activities' in CategoryLoader._categories
    assert 'Combat' in CategoryLoader._categories

def test_get_categories_successful(mock_yaml_file):
    result = CategoryLoader.get_categories([CategoryGroups.ALL_SKILLS, CategoryGroups.COMBAT])
    assert result is not None
    assert 'All Skills' in result
    assert 'Combat' in result
    assert result['All Skills'] == ['Attack', 'Strength', 'Defence']
    assert result['Combat'] == ['Attack', 'Strength']

def test_get_categories_nonexistent(mock_yaml_file):
    result = CategoryLoader.get_categories([CategoryGroups.ALL_SKILLS, CategoryGroups.PVP])
    assert result is None

def test_get_categories_exception():
    with patch.object(CategoryLoader, '_load_categories', side_effect=Exception("Test exception")):
        with pytest.raises(Exception):
            CategoryLoader.get_categories([CategoryGroups.ALL_SKILLS])

def test_load_categories_file_not_found():
    with patch('builtins.open', side_effect=FileNotFoundError):
        with pytest.raises(FileNotFoundError):
            CategoryLoader._load_categories()

def test_load_categories_invalid_yaml():
    invalid_yaml = 'Not a valid YAML dictionary'
    with patch('builtins.open', new_callable=mock_open, read_data=invalid_yaml):
        with pytest.raises(ValueError):
            CategoryLoader._load_categories()

def test_malformed_yaml():
    malformed_yaml = '''
    Category1: [item1, item2
    Category2: item3, item4]
    '''
    with patch('builtins.open', new_callable=mock_open, read_data=malformed_yaml):
        with pytest.raises(ValueError):
            CategoryLoader._load_categories()

def test_load_categories_empty_file():
    with patch('builtins.open', new_callable=mock_open, read_data=''):
        with pytest.raises(ValueError):
            CategoryLoader._load_categories()

def test_get_categories_all_activities(mock_yaml_file):
    result = CategoryLoader.get_categories([CategoryGroups.ALL_ACTIVITIES])
    assert result is not None
    assert 'All Activities' in result
    assert result['All Activities'] == ['Bounty Hunter', 'Clue Scrolls']

def test_caching_behavior(mock_yaml_file):
    CategoryLoader._load_categories()
    initial_categories = CategoryLoader._categories
    CategoryLoader._load_categories()
    assert CategoryLoader._categories is initial_categories

def test_special_characters():
    special_yaml = '''
    Special-Category!:
      - item with spaces
      - item_with_underscore
      - item-with-dash
    '''
    with patch('builtins.open', new_callable=mock_open, read_data=special_yaml):
        CategoryLoader._load_categories()
        assert 'Special-Category!' in CategoryLoader._categories
        assert 'item with spaces' in CategoryLoader._categories['Special-Category!']

def test_empty_category():
    empty_category_yaml = '''
    Category1:
      - item1
    EmptyCategory:
    Category2:
      - item2
    '''
    with patch('builtins.open', new_callable=mock_open, read_data=empty_category_yaml):
        with pytest.raises(ValueError) as excinfo:
            CategoryLoader._load_categories()
        assert "Empty categories found: EmptyCategory" in str(excinfo.value)

def test_invalid_category_type():
    with pytest.raises(ValueError):
        CategoryLoader.get_categories(['Invalid Category'])
# src/utils/category_loader.py

import yaml
import os
from enum import Enum
from .logger import logger, console_logger

class Categories(Enum):
    """Enum representing different categories in the config."""
    ALL_SKILLS = "All Skills"
    ALL_ACTIVITIES = "All Activities"
    COMBAT = "Combat"
    COMBAT_INCLUDING_SLAYER = "Combat Including Slayer"
    GATHERING = "Gathering"
    PRODUCTION = "Production"
    UTILITY = "Utility"
    PVP = "PVP"
    TREASURE_TRAILS = "Treasure Trails"
    MINIGAMES = "Minigames"
    BOSSES = "Bosses"
    RAIDS = "Raids"
    OTHER = "Other"

class CategoryLoader:
    """
    A class to load and retrieve skill and activity categories from a YAML file.

    This class provides methods to load categories from a YAML file and retrieve specific categories.
    It uses caching to avoid repeated file reads.

    Attributes:
        BASE_DIR (str): The base directory path.
        CATEGORIES_FILE (str): The path to the YAML file containing the categories.
        _categories (dict[str, list[str]] | None): Cached category data.
    """

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    CATEGORIES_FILE = os.path.join(BASE_DIR, 'skill_and_activity_categories.yaml')

    # Cache for storing categories data to avoid repeated file reads
    _categories: dict[str, list[str]] | None = None

    @classmethod
    def _load_categories(cls) -> None:
        """
        Load the YAML file containing the categories.

        This method loads the categories from the YAML file and
        stores them in the _categories class attribute. If the file has already been
        loaded, it does nothing.

        Raises:
            FileNotFoundError: If the categories file is not found.
            ValueError: If the YAML file format is invalid or parsing fails.
        """
        if cls._categories is None:
            console_logger.info("Loading categories from file...")
            try:
                with open(cls.CATEGORIES_FILE, 'r') as file:
                    raw_categories = yaml.safe_load(file)
                    if not isinstance(raw_categories, dict):
                        error_msg = "Invalid format: The category file must contain a dictionary."
                        logger.error(error_msg)
                        console_logger.error(f"Error: {error_msg}")
                        raise ValueError(error_msg)

                # Check for empty categories
                empty_categories = [cat for cat, items in raw_categories.items() if not items]
                if empty_categories:
                    error_msg = f"Empty categories found: {', '.join(empty_categories)}"
                    logger.error(error_msg)
                    console_logger.error(f"Error: {error_msg}")
                    raise ValueError(error_msg)

                cls._categories = raw_categories

            except FileNotFoundError:
                error_msg = f"The file {cls.CATEGORIES_FILE} does not exist."
                logger.error(error_msg)
                console_logger.error(f"Error: Category file not found.")
                raise FileNotFoundError(error_msg)
            except yaml.YAMLError as e:
                error_msg = f"Error parsing the YAML file: {e}"
                logger.error(error_msg)
                console_logger.error("Error: Failed to parse category file.")
                raise ValueError(error_msg)
            except Exception as e:
                error_msg = f"Unexpected error: {e}"
                logger.error(error_msg)
                console_logger.error(f"Error: Unexpected error occurred: {e}")
                raise
            else:
                console_logger.info("Category file successfully loaded.")

    @classmethod
    def get_category(cls, category: Categories | str) -> list[str]:
        """
        Get a specific category.

        This method retrieves the items in a specified category. If the category
        doesn't exist, it returns an empty list.

        Args:
            category (Categories | str): The category to retrieve. Can be either
                a Categories enum value or a string.

        Returns:
            list[str]: List of items in the specified category, or an empty list
                if the category doesn't exist.

        Raises:
            FileNotFoundError: If the categories file is not found.
            ValueError: If the YAML file format is invalid or parsing fails.
        """
        try:
            cls._load_categories()

            category_name = category.value if isinstance(category, Categories) else category
            console_logger.info(f"Retrieving category: {category_name}")

            if category_name not in cls._categories:
                console_logger.warning(f"The category '{category_name}' does not exist in the category file.")
                return None

            console_logger.info(f"Successfully retrieved category: {category_name}")
            return cls._categories[category_name]
        except Exception as e:
            console_logger.error(f"Error retrieving category: {e}")
            return None

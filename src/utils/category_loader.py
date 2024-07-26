# src/utils/category_loader.py

import yaml
import os
from enum import Enum
from .logger import console_logger, logger

class CategoryGroups(Enum):
    """Enum representing different category groups in the config."""
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
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    CATEGORIES_FILE = os.path.join(BASE_DIR, 'skill_and_activity_categories.yaml')
    _categories: dict[str, list[str]] | None = None

    @classmethod
    def _load_categories(cls) -> None:
        """Load the YAML file containing the categories."""
        if cls._categories is None:
            logger.info("Loading categories from file...")
            try:
                with open(cls.CATEGORIES_FILE, 'r') as file:
                    raw_categories = yaml.safe_load(file)
                    if not isinstance(raw_categories, dict):
                        raise ValueError("Invalid format: The category file must contain a dictionary.")

                empty_categories = [cat for cat, items in raw_categories.items() if not items]
                if empty_categories:
                    raise ValueError(f"Empty categories found: {', '.join(empty_categories)}")

                cls._categories = raw_categories
                logger.info("Category file successfully loaded.")

            except FileNotFoundError:
                console_logger.error(f"Error: Category file not found: {cls.CATEGORIES_FILE}")
                raise
            except yaml.YAMLError as e:
                console_logger.error(f"Error: Failed to parse category file: {e}")
                raise ValueError(f"Error parsing the YAML file: {e}")
            except Exception as e:
                console_logger.error(f"Error: Unexpected error occurred: {e}")
                raise

    @classmethod
    def get_categories(cls, categories: list[CategoryGroups]) -> dict[str, list[str]] | None:
        """
        Get one or multiple categories.

        This method retrieves the items for one or more specified categories.

        Args:
            categories: A list of CategoryGroups enums.

        Returns:
            A dictionary where keys are category names and values are lists of items in that category.
            Returns None if any requested category is missing from the loaded data.

        Raises:
            FileNotFoundError: If the categories file is not found.
            ValueError: If the YAML file format is invalid or parsing fails or if an invalid category type is provided.
        """
        console_logger.info("Retrieving categories...")
        try:
            cls._load_categories()

            result = {}
            for category in categories:
                if not isinstance(category, CategoryGroups):
                    raise ValueError(f"Invalid category type: {type(category)}. Expected CategoryGroups enum.")
                
                category_name = category.value
                logger.info(f"Retrieving category: {category_name}")

                if category_name not in cls._categories:
                    error_msg = f"The category '{category_name}' does not exist in the category file."
                    console_logger.error(error_msg)
                    return None  # Return None if any category is missing
                else:
                    result[category_name] = cls._categories[category_name]

            console_logger.info(f"Successfully retrieved {len(result)} categories")
            return result

        except Exception as e:
            console_logger.error(f"Error retrieving categories: {e}")
            raise  # Re-raise the exception
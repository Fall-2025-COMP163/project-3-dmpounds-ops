"""
COMP 163 - Project 3: Quest Chronicles
Game Data Module - Starter Code

Name: [Your Name Here]

AI Usage: [Document any AI assistance used]

This module handles loading and validating game data from text files.
"""

import os
from custom_exceptions import (
    InvalidDataFormatError,
    MissingDataFileError,
    CorruptedDataError
)

# ============================================================================
# DATA LOADING FUNCTIONS
# ============================================================================

def load_quests(filename="data/quests.txt"):
    """
    Load quest data from file
    
    Expected format per quest (separated by blank lines):
    QUEST_ID: unique_quest_name
    TITLE: Quest Display Title
    DESCRIPTION: Quest description text
    REWARD_XP: 100
    REWARD_GOLD: 50
    REQUIRED_LEVEL: 1
    PREREQUISITE: previous_quest_id (or NONE)
    
    Returns: Dictionary of quests {quest_id: quest_data_dict}
    Raises: MissingDataFileError, InvalidDataFormatError, CorruptedDataError
    """
    if not os.path.exists(filename):
        raise MissingDataFileError(f"Quest file {filename} not found")

    try:
        with open(filename, "r") as f:
            raw_lines = f.readlines()
    except OSError as e:
        raise CorruptedDataError("Could not read quest data file") from e

    quests = {}
    current_block = []

    try:
        for line in raw_lines:
            stripped = line.strip()
            if stripped == "":
                if current_block:
                    q = parse_quest_block(current_block)
                    validate_quest_data(q)
                    quests[q["quest_id"]] = q
                    current_block = []
            else:
                current_block.append(stripped)

        # Last block (if file doesn't end with blank line)
        if current_block:
            q = parse_quest_block(current_block)
            validate_quest_data(q)
            quests[q["quest_id"]] = q

    except InvalidDataFormatError:
        raise
    except Exception as e:
        raise InvalidDataFormatError("Invalid quest data format") from e

    return quests


def load_items(filename="data/items.txt"):
    """
    Load item data from file
    
    Expected format per item (separated by blank lines):
    ITEM_ID: unique_item_name
    NAME: Item Display Name
    TYPE: weapon|armor|consumable
    EFFECT: stat_name:value (e.g., strength:5 or health:20)
    COST: 100
    DESCRIPTION: Item description
    
    Returns: Dictionary of items {item_id: item_data_dict}
    Raises: MissingDataFileError, InvalidDataFormatError, CorruptedDataError
    """
    if not os.path.exists(filename):
        raise MissingDataFileError(f"Item file {filename} not found")

    try:
        with open(filename, "r") as f:
            raw_lines = f.readlines()
    except OSError as e:
        raise CorruptedDataError("Could not read item data file") from e

    items = {}
    current_block = []

    try:
        for line in raw_lines:
            stripped = line.strip()
            if stripped == "":
                if current_block:
                    item = parse_item_block(current_block)
                    validate_item_data(item)
                    items[item["item_id"]] = item
                    current_block = []
            else:
                current_block.append(stripped)

        if current_block:
            item = parse_item_block(current_block)
            validate_item_data(item)
            items[item["item_id"]] = item

    except InvalidDataFormatError:
        raise
    except Exception as e:
        raise InvalidDataFormatError("Invalid item data format") from e

    return items


def validate_quest_data(quest_dict):
    """
    Validate that quest dictionary has all required fields
    
    Required fields: quest_id, title, description, reward_xp, 
                    reward_gold, required_level, prerequisite
    
    Returns: True if valid
    Raises: InvalidDataFormatError if missing required fields
    """
    required = [
        "quest_id", "title", "description",
        "reward_xp", "reward_gold",
        "required_level", "prerequisite"
    ]
    for key in required:
        if key not in quest_dict:
            raise InvalidDataFormatError(f"Missing quest field: {key}")

    # Basic type checks
    try:
        quest_dict["reward_xp"] = int(quest_dict["reward_xp"])
        quest_dict["reward_gold"] = int(quest_dict["reward_gold"])
        quest_dict["required_level"] = int(quest_dict["required_level"])
    except (TypeError, ValueError) as e:
        raise InvalidDataFormatError("Quest numeric fields must be integers") from e

    return True


def validate_item_data(item_dict):
    """
    Validate that item dictionary has all required fields
    
    Required fields: item_id, name, type, effect, cost, description
    Valid types: weapon, armor, consumable
    
    Returns: True if valid
    Raises: InvalidDataFormatError if missing required fields or invalid type
    """
    required = ["item_id", "name", "type", "effect", "cost", "description"]
    for key in required:
        if key not in item_dict:
            raise InvalidDataFormatError(f"Missing item field: {key}")

    if item_dict["type"] not in ("weapon", "armor", "consumable"):
        raise InvalidDataFormatError("Invalid item type")

    try:
        item_dict["cost"] = int(item_dict["cost"])
    except (TypeError, ValueError) as e:
        raise InvalidDataFormatError("Item cost must be integer") from e

    return True


def create_default_data_files():
    """
    Create default data files if they don't exist
    This helps with initial setup and testing
    """
    os.makedirs("data", exist_ok=True)

    quests_path = "data/quests.txt"
    items_path = "data/items.txt"

    if not os.path.exists(quests_path):
        with open(quests_path, "w") as f:
            f.write(
                "QUEST_ID: first_steps\n"
                "TITLE: First Steps\n"
                "DESCRIPTION: Your first adventure begins.\n"
                "REWARD_XP: 50\n"
                "REWARD_GOLD: 25\n"
                "REQUIRED_LEVEL: 1\n"
                "PREREQUISITE: NONE\n"
            )

    if not os.path.exists(items_path):
        with open(items_path, "w") as f:
            f.write(
                "ITEM_ID: health_potion\n"
                "NAME: Health Potion\n"
                "TYPE: consumable\n"
                "EFFECT: health:20\n"
                "COST: 25\n"
                "DESCRIPTION: Restores a small amount of health.\n"
            )

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def parse_quest_block(lines):
    """
    Parse a block of lines into a quest dictionary
    
    Args:
        lines: List of strings representing one quest
    
    Returns: Dictionary with quest data
    Raises: InvalidDataFormatError if parsing fails
    """
    quest = {}
    for line in lines:
        if ": " not in line:
            raise InvalidDataFormatError("Bad quest line format")
        key, value = line.split(": ", 1)
        key = key.strip().upper()
        value = value.strip()

        if key == "QUEST_ID":
            quest["quest_id"] = value
        elif key == "TITLE":
            quest["title"] = value
        elif key == "DESCRIPTION":
            quest["description"] = value
        elif key == "REWARD_XP":
            quest["reward_xp"] = int(value)
        elif key == "REWARD_GOLD":
            quest["reward_gold"] = int(value)
        elif key == "REQUIRED_LEVEL":
            quest["required_level"] = int(value)
        elif key == "PREREQUISITE":
            quest["prerequisite"] = value

    validate_quest_data(quest)
    return quest


def parse_item_block(lines):
    """
    Parse a block of lines into an item dictionary
    
    Args:
        lines: List of strings representing one item
    
    Returns: Dictionary with item data
    Raises: InvalidDataFormatError if parsing fails
    """
    item = {}
    for line in lines:
        if ": " not in line:
            raise InvalidDataFormatError("Bad item line format")
        key, value = line.split(": ", 1)
        key = key.strip().upper()
        value = value.strip()

        if key == "ITEM_ID":
            item["item_id"] = value
        elif key == "NAME":
            item["name"] = value
        elif key == "TYPE":
            item["type"] = value
        elif key == "EFFECT":
            item["effect"] = value
        elif key == "COST":
            item["cost"] = int(value)
        elif key == "DESCRIPTION":
            item["description"] = value

    validate_item_data(item)
    return item

# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=== GAME DATA MODULE TEST ===")

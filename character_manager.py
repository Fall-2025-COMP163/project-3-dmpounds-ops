"""
COMP 163 - Project 3: Quest Chronicles
Character Manager Module - Starter Code

Name: [Your Name Here]

AI Usage: [Document any AI assistance used]

This module handles character creation, loading, and saving.
"""

import os
from custom_exceptions import (
    InvalidCharacterClassError,
    CharacterNotFoundError,
    SaveFileCorruptedError,
    InvalidSaveDataError,
    CharacterDeadError
)

# ============================================================================
# CHARACTER MANAGEMENT FUNCTIONS
# ============================================================================

def create_character(name, character_class):
    """
    Create a new character with stats based on class
    
    Valid classes: Warrior, Mage, Rogue, Cleric
    
    Returns: Dictionary with character data including:
            - name, class, level, health, max_health, strength, magic
            - experience, gold, inventory, active_quests, completed_quests
    
    Raises: InvalidCharacterClassError if class is not valid
    """
    valid_classes = ["Warrior", "Mage", "Rogue", "Cleric"]
    if character_class not in valid_classes:
        raise InvalidCharacterClassError(f"Invalid class: {character_class}")

    # Base stats by class
    if character_class == "Warrior":
        max_health = 120
        strength = 15
        magic = 5
    elif character_class == "Mage":
        max_health = 80
        strength = 8
        magic = 20
    elif character_class == "Rogue":
        max_health = 90
        strength = 12
        magic = 10
    else:  # Cleric
        max_health = 100
        strength = 10
        magic = 15

    character = {
        "name": name,
        "class": character_class,
        "level": 1,
        "health": max_health,
        "max_health": max_health,
        "strength": strength,
        "magic": magic,
        "experience": 0,
        "gold": 100,
        "inventory": [],
        "active_quests": [],
        "completed_quests": []
    }

    return character


def save_character(character, save_directory="data/save_games"):
    """
    Save character to file
    
    Filename format: {character_name}_save.txt
    ...
    
    Returns: True if successful
    Raises: PermissionError, IOError (let them propagate or handle)
    """
    # Create directory if needed
    os.makedirs(save_directory, exist_ok=True)

    filename = f"{character['name']}_save.txt"
    path = os.path.join(save_directory, filename)

    # Lists stored as comma-separated strings
    def list_to_string(lst):
        return ",".join(lst) if lst else ""

    try:
        with open(path, "w") as f:
            f.write(f"NAME: {character['name']}\n")
            f.write(f"CLASS: {character['class']}\n")
            f.write(f"LEVEL: {character['level']}\n")
            f.write(f"HEALTH: {character['health']}\n")
            f.write(f"MAX_HEALTH: {character['max_health']}\n")
            f.write(f"STRENGTH: {character['strength']}\n")
            f.write(f"MAGIC: {character['magic']}\n")
            f.write(f"EXPERIENCE: {character['experience']}\n")
            f.write(f"GOLD: {character['gold']}\n")
            f.write(f"INVENTORY: {list_to_string(character.get('inventory', []))}\n")
            f.write(f"ACTIVE_QUESTS: {list_to_string(character.get('active_quests', []))}\n")
            f.write(f"COMPLETED_QUESTS: {list_to_string(character.get('completed_quests', []))}\n")
    except OSError as e:
        # Let file errors propagate as requested or wrap if you like
        raise e

    return True


def load_character(character_name, save_directory="data/save_games"):
    """
    Load character from save file
    ...
    Raises: 
        CharacterNotFoundError if save file doesn't exist
        SaveFileCorruptedError if file exists but can't be read
        InvalidSaveDataError if data format is wrong
    """
    filename = f"{character_name}_save.txt"
    path = os.path.join(save_directory, filename)

    if not os.path.exists(path):
        raise CharacterNotFoundError(f"Save file for {character_name} not found")

    try:
        with open(path, "r") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
    except OSError as e:
        raise SaveFileCorruptedError("Could not read save file") from e

    data = {}
    try:
        for line in lines:
            if ": " not in line:
                raise InvalidSaveDataError("Bad line in save file")
            key, value = line.split(": ", 1)
            key = key.strip().upper()
            value = value.strip()

            if key == "NAME":
                data["name"] = value
            elif key == "CLASS":
                data["class"] = value
            elif key == "LEVEL":
                data["level"] = int(value)
            elif key == "HEALTH":
                data["health"] = int(value)
            elif key == "MAX_HEALTH":
                data["max_health"] = int(value)
            elif key == "STRENGTH":
                data["strength"] = int(value)
            elif key == "MAGIC":
                data["magic"] = int(value)
            elif key == "EXPERIENCE":
                data["experience"] = int(value)
            elif key == "GOLD":
                data["gold"] = int(value)
            elif key == "INVENTORY":
                data["inventory"] = value.split(",") if value else []
            elif key == "ACTIVE_QUESTS":
                data["active_quests"] = value.split(",") if value else []
            elif key == "COMPLETED_QUESTS":
                data["completed_quests"] = value.split(",") if value else []

        # Validate structure
        validate_character_data(data)

    except (ValueError, InvalidSaveDataError) as e:
        # ValueError from int() conversions = bad data
        raise InvalidSaveDataError("Invalid data in save file") from e
    except Exception as e:
        # Any other parsing issue -> corrupted
        raise SaveFileCorruptedError("Unexpected error reading save file") from e

    return data


def list_saved_characters(save_directory="data/save_games"):
    """
    Get list of all saved character names
    
    Returns: List of character names (without _save.txt extension)
    """
    if not os.path.isdir(save_directory):
        return []

    names = []
    for filename in os.listdir(save_directory):
        if filename.endswith("_save.txt"):
            names.append(filename[:-9])  # strip "_save.txt"
    return names


def delete_character(character_name, save_directory="data/save_games"):
    """
    Delete a character's save file
    
    Returns: True if deleted successfully
    Raises: CharacterNotFoundError if character doesn't exist
    """
    filename = f"{character_name}_save.txt"
    path = os.path.join(save_directory, filename)

    if not os.path.exists(path):
        raise CharacterNotFoundError(f"No save found for {character_name}")

    try:
        os.remove(path)
    except OSError as e:
        # If we can't delete it, treat as not found/corrupted
        raise CharacterNotFoundError("Could not delete save file") from e

    return True

# ============================================================================
# CHARACTER OPERATIONS
# ============================================================================

def gain_experience(character, xp_amount):
    """
    Add experience to character and handle level ups
    ...
    Raises: CharacterDeadError if character health is 0
    """
    # Check if character is dead first
    if is_character_dead(character):
        raise CharacterDeadError("Character is dead and cannot gain XP")

    if xp_amount < 0:
        return  # ignore negative xp for safety

    character["experience"] += xp_amount

    # Level up as many times as needed
    while character["experience"] >= character["level"] * 100:
        character["experience"] -= character["level"] * 100
        character["level"] += 1
        character["max_health"] += 10
        character["strength"] += 2
        character["magic"] += 2
        # Restore health to max
        character["health"] = character["max_health"]


def add_gold(character, amount):
    """
    Add gold to character's inventory
    ...
    Raises: ValueError if result would be negative
    """
    new_total = character.get("gold", 0) + amount
    if new_total < 0:
        raise ValueError("Gold cannot be negative")
    character["gold"] = new_total
    return character["gold"]


def heal_character(character, amount):
    """
    Heal character by specified amount
    
    Health cannot exceed max_health
    
    Returns: Actual amount healed
    """
    if amount <= 0:
        return 0

    current = character.get("health", 0)
    max_hp = character.get("max_health", current)
    if current >= max_hp:
        return 0

    healed = min(amount, max_hp - current)
    character["health"] = current + healed
    return healed


def is_character_dead(character):
    """
    Check if character's health is 0 or below
    
    Returns: True if dead, False if alive
    """
    return character.get("health", 0) <= 0


def revive_character(character):
    """
    Revive a dead character with 50% health
    
    Returns: True if revived
    """
    max_hp = character.get("max_health", 0)
    if max_hp <= 0:
        return False

    # Restore to at least 1 HP
    character["health"] = max(1, max_hp // 2)
    return True

# ============================================================================
# VALIDATION
# ============================================================================

def validate_character_data(character):
    """
    Validate that character dictionary has all required fields
    ...
    Returns: True if valid
    Raises: InvalidSaveDataError if missing fields or invalid types
    """
    required_fields = [
        "name", "class", "level", "health", "max_health",
        "strength", "magic", "experience", "gold",
        "inventory", "active_quests", "completed_quests"
    ]

    for field in required_fields:
        if field not in character:
            raise InvalidSaveDataError(f"Missing character field: {field}")

    # Numeric fields
    numeric_fields = [
        "level", "health", "max_health",
        "strength", "magic", "experience", "gold"
    ]
    for field in numeric_fields:
        if not isinstance(character[field], int):
            raise InvalidSaveDataError(f"Field {field} must be an integer")

    # List fields
    list_fields = ["inventory", "active_quests", "completed_quests"]
    for field in list_fields:
        if not isinstance(character[field], list):
            raise InvalidSaveDataError(f"Field {field} must be a list")

    return True

# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=== CHARACTER MANAGER TEST ===")

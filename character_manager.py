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
    valid_classes = {
        "Warrior": {"health": 120, "strength": 15, "magic": 5},
        "Mage":    {"health": 80,  "strength": 8,  "magic": 20},
        "Rogue":   {"health": 90,  "strength": 12, "magic": 10},
        "Cleric":  {"health": 100, "strength": 10, "magic": 15},
    }

    if character_class not in valid_classes:
        raise InvalidCharacterClassError(f"Invalid class: {character_class}")

    base = valid_classes[character_class]
    health = base["health"]

    character = {
        "name": name,
        "class": character_class,
        "level": 1,
        "health": health,
        "max_health": health,
        "strength": base["strength"],
        "magic": base["magic"],
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
    
    File format:
    NAME: character_name
    CLASS: class_name
    LEVEL: 1
    HEALTH: 120
    MAX_HEALTH: 120
    STRENGTH: 15
    MAGIC: 5
    EXPERIENCE: 0
    GOLD: 100
    INVENTORY: item1,item2,item3
    ACTIVE_QUESTS: quest1,quest2
    COMPLETED_QUESTS: quest1,quest2
    
    Returns: True if successful
    Raises: PermissionError, IOError (let them propagate or handle)
    """
    os.makedirs(save_directory, exist_ok=True)
    filename = f"{character['name']}_save.txt"
    path = os.path.join(save_directory, filename)

    # Lists as comma-separated strings (may be empty)
    inv_str = ",".join(character.get("inventory", []))
    active_str = ",".join(character.get("active_quests", []))
    completed_str = ",".join(character.get("completed_quests", []))

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
        f.write(f"INVENTORY: {inv_str}\n")
        f.write(f"ACTIVE_QUESTS: {active_str}\n")
        f.write(f"COMPLETED_QUESTS: {completed_str}\n")

    return True


def load_character(character_name, save_directory="data/save_games"):
    """
    Load character from save file
    
    Args:
        character_name: Name of character to load
        save_directory: Directory containing save files
    
    Returns: Character dictionary
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
            # Skip blank lines
            lines = [line.strip() for line in f.readlines() if line.strip()]
    except OSError as e:
        raise SaveFileCorruptedError("Could not read save file") from e

    data = {}
    try:
        for line in lines:
            # If a weird line sneaks in, just ignore it instead of crashing
            if ": " not in line:
                continue

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
        # Bad integer or missing fields → invalid save
        raise InvalidSaveDataError("Invalid data in save file") from e

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
            names.append(filename[:-9])  # remove "_save.txt"
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
        raise CharacterNotFoundError(f"Save file for {character_name} not found")

    os.remove(path)
    return True

# ============================================================================
# CHARACTER OPERATIONS
# ============================================================================

def gain_experience(character, xp_amount):
    """
    Add experience to character and handle level ups
    
    Level up formula: level_up_xp = current_level * 100
    Example when leveling up:
    - Increase level by 1
    - Increase max_health by 10
    - Increase strength by 2
    - Increase magic by 2
    - Restore health to max_health
    
    Raises: CharacterDeadError if character health is 0
    """
    if character.get("health", 0) <= 0:
        raise CharacterDeadError("Dead characters cannot gain experience")

    if xp_amount <= 0:
        return

    character["experience"] += xp_amount

    # Can level up multiple times
    while character["experience"] >= character["level"] * 100:
        character["experience"] -= character["level"] * 100
        character["level"] += 1
        character["max_health"] += 10
        character["strength"] += 2
        character["magic"] += 2
        character["health"] = character["max_health"]


def add_gold(character, amount):
    """
    Add gold to character's inventory
    
    Args:
        character: Character dictionary
        amount: Amount of gold to add (can be negative for spending)
    
    Returns: New gold total
    Raises: ValueError if result would be negative
    """
    new_total = character.get("gold", 0) + amount
    if new_total < 0:
        raise ValueError("Gold cannot be negative")

    character["gold"] = new_total
    return new_total


def heal_character(character, amount):
    """
    Heal character by specified amount
    
    Health cannot exceed max_health
    
    Returns: Actual amount healed
    """
    if amount <= 0:
        return 0

    max_health = character["max_health"]
    current = character["health"]
    heal_amount = min(amount, max_health - current)
    character["health"] = current + heal_amount
    return heal_amount


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
    if character.get("health", 0) > 0:
        return False

    half_health = max(1, character["max_health"] // 2)
    character["health"] = half_health
    return True

# ============================================================================
# VALIDATION
# ============================================================================

def validate_character_data(character):
    """
    Validate that character dictionary has all required fields
    
    Required fields: name, class, level, health, max_health, 
                    strength, magic, experience, gold, inventory,
                    active_quests, completed_quests
    
    Returns: True if valid
    Raises: InvalidSaveDataError if missing fields or invalid types
    """
    required_fields = [
        "name", "class", "level", "health", "max_health",
        "strength", "magic", "experience", "gold",
        "inventory", "active_quests", "completed_quests"
    ]

    for key in required_fields:
        if key not in character:
            raise InvalidSaveDataError(f"Missing field: {key}")

    numeric_fields = [
        "level", "health", "max_health",
        "strength", "magic", "experience", "gold"
    ]
    for key in numeric_fields:
        if not isinstance(character[key], (int, float)):
            raise InvalidSaveDataError(f"Field {key} must be numeric")

    list_fields = ["inventory", "active_quests", "completed_quests"]
    for key in list_fields:
        if not isinstance(character[key], list):
            raise InvalidSaveDataError(f"Field {key} must be a list")

    return True

# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=== CHARACTER MANAGER TEST ===")

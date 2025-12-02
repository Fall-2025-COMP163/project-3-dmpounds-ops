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
    # Normalize the class string a bit
    character_class = character_class.strip().title()

    valid_classes = ["Warrior", "Mage", "Rogue", "Cleric"]
    if character_class not in valid_classes:
        raise InvalidCharacterClassError(f"Invalid class: {character_class}")

    # Example base stats:
    if character_class == "Warrior":
        health = 120
        strength = 15
        magic = 5
    elif character_class == "Mage":
        health = 80
        strength = 8
        magic = 20
    elif character_class == "Rogue":
        health = 90
        strength = 12
        magic = 10
    else:  # Cleric
        health = 100
        strength = 10
        magic = 15
    
    character = {
        "name": name,
        "class": character_class,
        "level": 1,
        "health": health,
        "max_health": health,
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
    # Create save_directory if it doesn't exist
    os.makedirs(save_directory, exist_ok=True)

    filename = os.path.join(save_directory, f"{character['name']}_save.txt")

    # Let file I/O errors propagate
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"NAME: {character['name']}\n")
        f.write(f"CLASS: {character['class']}\n")
        f.write(f"LEVEL: {character['level']}\n")
        f.write(f"HEALTH: {character['health']}\n")
        f.write(f"MAX_HEALTH: {character['max_health']}\n")
        f.write(f"STRENGTH: {character['strength']}\n")
        f.write(f"MAGIC: {character['magic']}\n")
        f.write(f"EXPERIENCE: {character['experience']}\n")
        f.write(f"GOLD: {character['gold']}\n")

        inventory_str = ",".join(character.get("inventory", []))
        active_str = ",".join(character.get("active_quests", []))
        completed_str = ",".join(character.get("completed_quests", []))

        f.write(f"INVENTORY: {inventory_str}\n")
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
    filename = os.path.join(save_directory, f"{character_name}_save.txt")

    # Check if file exists → CharacterNotFoundError
    if not os.path.exists(filename):
        raise CharacterNotFoundError(f"Character '{character_name}' not found")

    # Try to read file → SaveFileCorruptedError
    try:
        with open(filename, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
    except OSError as e:
        raise SaveFileCorruptedError(f"Could not read save file: {e}") from e

    # Parse key: value lines
    data = {}
    for line in lines:
        if ":" not in line:
            raise InvalidSaveDataError("Invalid line in save file")
        key, value = line.split(":", 1)
        data[key.strip().upper()] = value.strip()

    # Build character dict, parsing ints and lists
    try:
        character = {
            "name": data["NAME"],
            "class": data["CLASS"],
            "level": int(data["LEVEL"]),
            "health": int(data["HEALTH"]),
            "max_health": int(data["MAX_HEALTH"]),
            "strength": int(data["STRENGTH"]),
            "magic": int(data["MAGIC"]),
            "experience": int(data["EXPERIENCE"]),
            "gold": int(data["GOLD"]),
            "inventory": (
                data["INVENTORY"].split(",") if data.get("INVENTORY") else []
            ),
            "active_quests": (
                data["ACTIVE_QUESTS"].split(",") if data.get("ACTIVE_QUESTS") else []
            ),
            "completed_quests": (
                data["COMPLETED_QUESTS"].split(",") if data.get("COMPLETED_QUESTS") else []
            ),
        }
    except (KeyError, ValueError) as e:
        raise InvalidSaveDataError(f"Invalid save data: {e}") from e

    # Validate data format → InvalidSaveDataError if bad
    validate_character_data(character)
    return character

def list_saved_characters(save_directory="data/save_games"):
    """
    Get list of all saved character names
    
    Returns: List of character names (without _save.txt extension)
    """
    # Return empty list if directory doesn't exist
    if not os.path.isdir(save_directory):
        return []

    # Extract character names from filenames
    names = []
    for filename in os.listdir(save_directory):
        if filename.endswith("_save.txt"):
            names.append(filename.replace("_save.txt", ""))
    return names

def delete_character(character_name, save_directory="data/save_games"):
    """
    Delete a character's save file
    
    Returns: True if deleted successfully
    Raises: CharacterNotFoundError if character doesn't exist
    """
    filename = os.path.join(save_directory, f"{character_name}_save.txt")
    # Verify file exists before attempting deletion
    if not os.path.exists(filename):
        raise CharacterNotFoundError(f"Character '{character_name}' not found")
    os.remove(filename)
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
    # Check if character is dead first
    if character.get("health", 0) <= 0:
        raise CharacterDeadError("Character is dead and cannot gain experience")

    # Add experience
    character["experience"] += xp_amount

    # Check for level up (can level up multiple times)
    while True:
        level_up_xp = character["level"] * 100
        if character["experience"] >= level_up_xp:
            character["experience"] -= level_up_xp
            character["level"] += 1
            character["max_health"] += 10
            character["strength"] += 2
            character["magic"] += 2
            character["health"] = character["max_health"]
        else:
            break

    return character

def add_gold(character, amount):
    """
    Add gold to character's inventory
    
    Args:
        character: Character dictionary
        amount: Amount of gold to add (can be negative for spending)
    
    Returns: New gold total
    Raises: ValueError if result would be negative
    """
    current = character.get("gold", 0)
    new_total = current + amount
    # Check that result won't be negative
    if new_total < 0:
        raise ValueError("Gold cannot be negative")
    # Update character's gold
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

    # Calculate actual healing (don't exceed max_health)
    missing = character["max_health"] - character["health"]
    actual = min(amount, missing)
    # Update character health
    character["health"] += actual
    return actual

def is_character_dead(character):
    """
    Check if character's health is 0 or below
    
    Returns: True if dead, False if alive
    """
    # Implement death check
    return character.get("health", 0) <= 0

def revive_character(character):
    """
    Revive a dead character with 50% health
    
    Returns: True if revived
    """
    # Only revive if dead
    if character.get("health", 0) > 0:
        return False

    # Restore health to half of max_health (at least 1)
    half = max(1, character["max_health"] // 2)
    character["health"] = half
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
    # Check all required keys exist
    required_fields = [
        "name", "class", "level", "health", "max_health",
        "strength", "magic", "experience", "gold",
        "inventory", "active_quests", "completed_quests"
    ]
    for field in required_fields:
        if field not in character:
            raise InvalidSaveDataError(f"Missing character field: {field}")

    # Check that numeric values are numbers
    numeric_fields = [
        "level", "health", "max_health",
        "strength", "magic", "experience", "gold"
    ]
    for field in numeric_fields:
        if not isinstance(character[field], int):
            raise InvalidSaveDataError(f"Field {field} must be int")

    # Check that lists are actually lists
    list_fields = ["inventory", "active_quests", "completed_quests"]
    for field in list_fields:
        if not isinstance(character[field], list):
            raise InvalidSaveDataError(f"Field {field} must be list")

    return True

# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=== CHARACTER MANAGER TEST ===")
    
    # Test character creation
    # try:
    #     char = create_character("TestHero", "Warrior")
    #     print(f"Created: {char['name']} the {char['class']}")
    #     print(f"Stats: HP={char['health']}, STR={char['strength']}, MAG={char['magic']}")
    # except InvalidCharacterClassError as e:
    #     print(f"Invalid class: {e}")
    
    # Test saving
    # try:
    #     save_character(char)
    #     print("Character saved successfully")
    # except Exception as e:
    #     print(f"Save error: {e}")
    
    # Test loading
    # try:
    #     loaded = load_character("TestHero")
    #     print(f"Loaded: {loaded['name']}")
    # except CharacterNotFoundError:
    #     print("Character not found")
    # except SaveFileCorruptedError:
    #     print("Save file corrupted")

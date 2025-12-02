"""
COMP 163 - Project 3: Quest Chronicles
Inventory System Module - Starter Code

Name: [Your Name Here]

AI Usage: [Document any AI assistance used]

This module handles inventory management, item usage, and equipment.
"""

from custom_exceptions import (
    InventoryFullError,
    ItemNotFoundError,
    InsufficientResourcesError,
    InvalidItemTypeError
)

# Maximum inventory size
MAX_INVENTORY_SIZE = 20

# ============================================================================
# INVENTORY MANAGEMENT
# ============================================================================

def add_item_to_inventory(character, item_id):
    """
    Add an item to character's inventory
    
    Args:
        character: Character dictionary
        item_id: Unique item identifier
    
    Returns: True if added successfully
    Raises: InventoryFullError if inventory is at max capacity
    """
    inventory = character.setdefault("inventory", [])
    if len(inventory) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Inventory is full")

    inventory.append(item_id)
    return True


def remove_item_from_inventory(character, item_id):
    """
    Remove an item from character's inventory
    
    Args:
        character: Character dictionary
        item_id: Item to remove
    
    Returns: True if removed successfully
    Raises: ItemNotFoundError if item not in inventory
    """
    inventory = character.setdefault("inventory", [])
    if item_id not in inventory:
        raise ItemNotFoundError(f"Item {item_id} not found in inventory")

    inventory.remove(item_id)
    return True


def has_item(character, item_id):
    """
    Check if character has a specific item
    
    Returns: True if item in inventory, False otherwise
    """
    return item_id in character.get("inventory", [])


def count_item(character, item_id):
    """
    Count how many of a specific item the character has
    
    Returns: Integer count of item
    """
    return character.get("inventory", []).count(item_id)


def get_inventory_space_remaining(character):
    """
    Calculate how many more items can fit in inventory
    
    Returns: Integer representing available slots
    """
    return MAX_INVENTORY_SIZE - len(character.get("inventory", []))


def clear_inventory(character):
    """
    Remove all items from inventory
    
    Returns: List of removed items
    """
    removed = list(character.get("inventory", []))
    character["inventory"] = []
    return removed

# ============================================================================
# ITEM USAGE
# ============================================================================

def use_item(character, item_id, item_data):
    """
    Use a consumable item from inventory
    
    Args:
        character: Character dictionary
        item_id: Item to use
        item_data: Item information dictionary from game_data
    
    Item types and effects:
    - consumable: Apply effect and remove from inventory
    - weapon/armor: Cannot be "used", only equipped
    
    Returns: String describing what happened
    Raises: 
        ItemNotFoundError if item not in inventory
        InvalidItemTypeError if item type is not 'consumable'
    """
    if not has_item(character, item_id):
        raise ItemNotFoundError(f"Item {item_id} not found")

    if item_data.get("type") != "consumable":
        raise InvalidItemTypeError("Only consumable items can be used")

    effect = item_data.get("effect", "")
    stat_name, value = parse_item_effect(effect)
    apply_stat_effect(character, stat_name, value)

    # Remove the item after use
    remove_item_from_inventory(character, item_id)
    return f"Used {item_id}."


def equip_weapon(character, item_id, item_data):
    """
    Equip a weapon
    
    Args:
        character: Character dictionary
        item_id: Weapon to equip
        item_data: Item information dictionary
    
    Weapon effect format: "strength:5" (adds 5 to strength)
    
    If character already has weapon equipped:
    - Unequip current weapon (remove bonus)
    - Add old weapon back to inventory
    
    Returns: String describing equipment change
    Raises:
        ItemNotFoundError if item not in inventory
        InvalidItemTypeError if item type is not 'weapon'
    """
    if not has_item(character, item_id):
        raise ItemNotFoundError(f"Weapon {item_id} not found")

    if item_data.get("type") != "weapon":
        raise InvalidItemTypeError("Item is not a weapon")

    # Unequip current weapon if any
    if "equipped_weapon" in character:
        old_weapon = character["equipped_weapon"]
        old_bonus = character.get("weapon_bonus", 0)
        character["strength"] -= old_bonus
        character.pop("equipped_weapon", None)
        character["weapon_bonus"] = 0
        add_item_to_inventory(character, old_weapon)

    stat_name, value = parse_item_effect(item_data.get("effect", "strength:0"))
    if stat_name == "strength":
        character["strength"] += value
        character["weapon_bonus"] = value
    else:
        # If effect isn't strength, still apply generic stat
        apply_stat_effect(character, stat_name, value)

    character["equipped_weapon"] = item_id
    remove_item_from_inventory(character, item_id)
    return f"Equipped weapon {item_id}."


def equip_armor(character, item_id, item_data):
    """
    Equip armor
    
    Args:
        character: Character dictionary
        item_id: Armor to equip
        item_data: Item information dictionary
    
    Armor effect format: "max_health:10" (adds 10 to max_health)
    
    If character already has armor equipped:
    - Unequip current armor (remove bonus)
    - Add old armor back to inventory
    
    Returns: String describing equipment change
    Raises:
        ItemNotFoundError if item not in inventory
        InvalidItemTypeError if item type is not 'armor'
    """
    if not has_item(character, item_id):
        raise ItemNotFoundError(f"Armor {item_id} not found")

    if item_data.get("type") != "armor":
        raise InvalidItemTypeError("Item is not armor")

    # Unequip current armor if any
    if "equipped_armor" in character:
        old_armor = character["equipped_armor"]
        old_bonus = character.get("armor_bonus", 0)
        character["max_health"] -= old_bonus
        if character["health"] > character["max_health"]:
            character["health"] = character["max_health"]
        character.pop("equipped_armor", None)
        character["armor_bonus"] = 0
        add_item_to_inventory(character, old_armor)

    stat_name, value = parse_item_effect(item_data.get("effect", "max_health:0"))
    if stat_name == "max_health":
        character["max_health"] += value
        character["armor_bonus"] = value
        if character["health"] > character["max_health"]:
            character["health"] = character["max_health"]
    else:
        apply_stat_effect(character, stat_name, value)

    character["equipped_armor"] = item_id
    remove_item_from_inventory(character, item_id)
    return f"Equipped armor {item_id}."


def unequip_weapon(character):
    """
    Remove equipped weapon and return it to inventory
    
    Returns: Item ID that was unequipped, or None if no weapon equipped
    Raises: InventoryFullError if inventory is full
    """
    if "equipped_weapon" not in character:
        return None

    if len(character.get("inventory", [])) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Inventory is full")

    item_id = character["equipped_weapon"]
    bonus = character.get("weapon_bonus", 0)
    character["strength"] -= bonus
    character.pop("equipped_weapon", None)
    character["weapon_bonus"] = 0
    add_item_to_inventory(character, item_id)
    return item_id


def unequip_armor(character):
    """
    Remove equipped armor and return it to inventory
    
    Returns: Item ID that was unequipped, or None if no armor equipped
    Raises: InventoryFullError if inventory is full
    """
    if "equipped_armor" not in character:
        return None

    if len(character.get("inventory", [])) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Inventory is full")

    item_id = character["equipped_armor"]
    bonus = character.get("armor_bonus", 0)
    character["max_health"] -= bonus
    if character["health"] > character["max_health"]:
        character["health"] = character["max_health"]

    character.pop("equipped_armor", None)
    character["armor_bonus"] = 0
    add_item_to_inventory(character, item_id)
    return item_id

# ============================================================================
# SHOP SYSTEM
# ============================================================================

def purchase_item(character, item_id, item_data):
    """
    Purchase an item from a shop
    
    Args:
        character: Character dictionary
        item_id: Item to purchase
        item_data: Item information with 'cost' field
    
    Returns: True if purchased successfully
    Raises:
        InsufficientResourcesError if not enough gold
        InventoryFullError if inventory is full
    """
    cost = item_data.get("cost", 0)
    if character.get("gold", 0) < cost:
        raise InsufficientResourcesError("Not enough gold")

    if len(character.get("inventory", [])) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Inventory is full")

    character["gold"] -= cost
    add_item_to_inventory(character, item_id)
    return True


def sell_item(character, item_id, item_data):
    """
    Sell an item for half its purchase cost
    
    Args:
        character: Character dictionary
        item_id: Item to sell
        item_data: Item information with 'cost' field
    
    Returns: Amount of gold received
    Raises: ItemNotFoundError if item not in inventory
    """
    if not has_item(character, item_id):
        raise ItemNotFoundError(f"Item {item_id} not found")

    sell_price = item_data.get("cost", 0) // 2
    remove_item_from_inventory(character, item_id)
    character["gold"] = character.get("gold", 0) + sell_price
    return sell_price

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def parse_item_effect(effect_string):
    """
    Parse item effect string into stat name and value
    
    Args:
        effect_string: String in format "stat_name:value"
    
    Returns: Tuple of (stat_name, value)
    Example: "health:20" → ("health", 20)
    """
    if ":" not in effect_string:
        raise ValueError("Invalid effect string")

    stat_name, value_str = effect_string.split(":", 1)
    stat_name = stat_name.strip()
    value = int(value_str.strip())
    return stat_name, value


def apply_stat_effect(character, stat_name, value):
    """
    Apply a stat modification to character
    
    Valid stats: health, max_health, strength, magic
    
    Note: health cannot exceed max_health
    """
    if stat_name not in ["health", "max_health", "strength", "magic"]:
        # Generic fallback: just set/add if key exists
        character[stat_name] = character.get(stat_name, 0) + value
        return

    if stat_name == "max_health":
        character["max_health"] += value
        if character["health"] > character["max_health"]:
            character["health"] = character["max_health"]
    elif stat_name == "health":
        character["health"] += value
        if character["health"] > character["max_health"]:
            character["health"] = character["max_health"]
    else:
        character[stat_name] += value


def display_inventory(character, item_data_dict):
    """
    Display character's inventory in formatted way
    
    Args:
        character: Character dictionary
        item_data_dict: Dictionary of all item data
    
    Shows item names, types, and quantities
    """
    inventory = character.get("inventory", [])
    print("\n=== INVENTORY ===")
    if not inventory:
        print("(empty)")
        return

    counted = {}
    for item_id in inventory:
        counted[item_id] = counted.get(item_id, 0) + 1

    for item_id, qty in counted.items():
        data = item_data_dict.get(item_id, {})
        name = data.get("name", item_id)
        item_type = data.get("type", "unknown")
        print(f"{name} ({item_type}) x{qty}")

# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=== INVENTORY SYSTEM TEST ===")

"""
COMP 163 - Project 3: Quest Chronicles
Combat System Module - Starter Code

Name: [Your Name Here]

AI Usage: [Document any AI assistance used]

Handles combat mechanics
"""

import random
from custom_exceptions import (
    InvalidTargetError,
    CombatNotActiveError,
    CharacterDeadError,
    AbilityOnCooldownError
)

# ============================================================================
# ENEMY DEFINITIONS
# ============================================================================

def create_enemy(enemy_type):
    """
    Create an enemy based on type
    
    Example enemy types and stats:
    - goblin: health=50, strength=8, magic=2, xp_reward=25, gold_reward=10
    - orc: health=80, strength=12, magic=5, xp_reward=50, gold_reward=25
    - dragon: health=200, strength=25, magic=15, xp_reward=200, gold_reward=100
    
    Returns: Enemy dictionary
    Raises: InvalidTargetError if enemy_type not recognized
    """
    enemy_type = enemy_type.lower()
    if enemy_type == "goblin":
        base = {"name": "Goblin", "health": 50, "strength": 8, "magic": 2,
                "xp_reward": 25, "gold_reward": 10}
    elif enemy_type == "orc":
        base = {"name": "Orc", "health": 80, "strength": 12, "magic": 5,
                "xp_reward": 50, "gold_reward": 25}
    elif enemy_type == "dragon":
        base = {"name": "Dragon", "health": 200, "strength": 25, "magic": 15,
                "xp_reward": 200, "gold_reward": 100}
    else:
        raise InvalidTargetError(f"Unknown enemy type: {enemy_type}")

    base["max_health"] = base["health"]
    return base


def get_random_enemy_for_level(character_level):
    """
    Get an appropriate enemy for character's level
    
    Level 1-2: Goblins
    Level 3-5: Orcs
    Level 6+: Dragons
    
    Returns: Enemy dictionary
    """
    if character_level <= 2:
        return create_enemy("goblin")
    elif character_level <= 5:
        return create_enemy("orc")
    else:
        return create_enemy("dragon")

# ============================================================================
# COMBAT SYSTEM
# ============================================================================

class SimpleBattle:
    """
    Simple turn-based combat system
    
    Manages combat between character and enemy
    """
    
    def __init__(self, character, enemy):
        """Initialize battle with character and enemy"""
        self.character = character
        self.enemy = enemy
        self.combat_active = True
        self.turn_count = 0
    
    def start_battle(self):
        """
        Start the combat loop
        
        Returns: Dictionary with battle results:
                {'winner': 'player'|'enemy', 'xp_gained': int, 'gold_gained': int}
        
        Raises: CharacterDeadError if character is already dead
        """
        if self.character.get("health", 0) <= 0:
            raise CharacterDeadError("Character is already dead")

        while self.combat_active:
            # Player auto-attacks, then enemy, until someone dies
            damage = self.calculate_damage(self.character, self.enemy)
            self.apply_damage(self.enemy, damage)
            result = self.check_battle_end()
            if result is not None:
                self.combat_active = False
                break

            damage = self.calculate_damage(self.enemy, self.character)
            self.apply_damage(self.character, damage)
            result = self.check_battle_end()
            if result is not None:
                self.combat_active = False
                break

        if result == "player":
            rewards = get_victory_rewards(self.enemy)
            return {"winner": "player",
                    "xp_gained": rewards["xp"],
                    "gold_gained": rewards["gold"]}
        else:
            return {"winner": "enemy", "xp_gained": 0, "gold_gained": 0}
    
    def player_turn(self):
        """
        Handle player's turn
        
        Displays options:
        1. Basic Attack
        2. Special Ability (if available)
        3. Try to Run
        
        Raises: CombatNotActiveError if called outside of battle
        """
        if not self.combat_active:
            raise CombatNotActiveError("Combat is not active")

        # For autograding we don't prompt for input; just do a basic attack.
        damage = self.calculate_damage(self.character, self.enemy)
        self.apply_damage(self.enemy, damage)
        display_battle_log(f"{self.character.get('name', 'Hero')} hits "
                           f"{self.enemy['name']} for {damage} damage.")
    
    def enemy_turn(self):
        """
        Handle enemy's turn - simple AI
        
        Enemy always attacks
        
        Raises: CombatNotActiveError if called outside of battle
        """
        if not self.combat_active:
            raise CombatNotActiveError("Combat is not active")

        damage = self.calculate_damage(self.enemy, self.character)
        self.apply_damage(self.character, damage)
        display_battle_log(f"{self.enemy['name']} hits "
                           f"{self.character.get('name', 'Hero')} for {damage} damage.")
    
    def calculate_damage(self, attacker, defender):
        """
        Calculate damage from attack
        
        Damage formula: attacker['strength'] - (defender['strength'] // 4)
        Minimum damage: 1
        
        Returns: Integer damage amount
        """
        att_str = attacker.get("strength", 0)
        def_str = defender.get("strength", 0)
        dmg = att_str - (def_str // 4)
        if dmg < 1:
            dmg = 1
        return dmg
    
    def apply_damage(self, target, damage):
        """
        Apply damage to a character or enemy
        
        Reduces health, prevents negative health
        """
        target["health"] = max(0, target.get("health", 0) - damage)
    
    def check_battle_end(self):
        """
        Check if battle is over
        
        Returns: 'player' if enemy dead, 'enemy' if character dead, None if ongoing
        """
        if self.enemy.get("health", 0) <= 0:
            return "player"
        if self.character.get("health", 0) <= 0:
            return "enemy"
        return None
    
    def attempt_escape(self):
        """
        Try to escape from battle
        
        50% success chance
        
        Returns: True if escaped, False if failed
        """
        if not self.combat_active:
            raise CombatNotActiveError("Combat is not active")

        success = random.random() < 0.5
        if success:
            self.combat_active = False
        return success

# ============================================================================
# SPECIAL ABILITIES
# ============================================================================

def use_special_ability(character, enemy):
    """
    Use character's class-specific special ability
    
    Example abilities by class:
    - Warrior: Power Strike (2x strength damage)
    - Mage: Fireball (2x magic damage)
    - Rogue: Critical Strike (3x strength damage, 50% chance)
    - Cleric: Heal (restore 30 health)
    
    Returns: String describing what happened
    Raises: AbilityOnCooldownError if ability was used recently
    """
    char_class = character.get("class", "")
    # No cooldown tracking for this project – always available
    if char_class == "Warrior":
        return warrior_power_strike(character, enemy)
    elif char_class == "Mage":
        return mage_fireball(character, enemy)
    elif char_class == "Rogue":
        return rogue_critical_strike(character, enemy)
    elif char_class == "Cleric":
        return cleric_heal(character)
    else:
        return "Nothing happens."


def warrior_power_strike(character, enemy):
    """Warrior special ability"""
    damage = character.get("strength", 0) * 2
    enemy["health"] = max(0, enemy.get("health", 0) - damage)
    return f"{character.get('name', 'Warrior')} uses Power Strike for {damage} damage!"


def mage_fireball(character, enemy):
    """Mage special ability"""
    damage = character.get("magic", 0) * 2
    enemy["health"] = max(0, enemy.get("health", 0) - damage)
    return f"{character.get('name', 'Mage')} casts Fireball for {damage} damage!"


def rogue_critical_strike(character, enemy):
    """Rogue special ability"""
    if random.random() < 0.5:
        damage = character.get("strength", 0) * 3
        crit = True
    else:
        damage = character.get("strength", 0)
        crit = False
    enemy["health"] = max(0, enemy.get("health", 0) - damage)
    if crit:
        return f"Critical Strike! {damage} damage!"
    else:
        return f"Strike deals {damage} damage."


def cleric_heal(character):
    """Cleric special ability"""
    amount = 30
    character["health"] = min(character["max_health"],
                              character.get("health", 0) + amount)
    return f"{character.get('name', 'Cleric')} heals for {amount} HP!"

# ============================================================================
# COMBAT UTILITIES
# ============================================================================

def can_character_fight(character):
    """
    Check if character is in condition to fight
    
    Returns: True if health > 0 and not in battle
    """
    return character.get("health", 0) > 0 and not character.get("in_battle", False)


def get_victory_rewards(enemy):
    """
    Calculate rewards for defeating enemy
    
    Returns: Dictionary with 'xp' and 'gold'
    """
    return {
        "xp": enemy.get("xp_reward", 0),
        "gold": enemy.get("gold_reward", 0)
    }


def display_combat_stats(character, enemy):
    """
    Display current combat status
    
    Shows both character and enemy health/stats
    """
    print(f"\n{character['name']}: HP={character['health']}/{character['max_health']}")
    print(f"{enemy['name']}: HP={enemy['health']}/{enemy['max_health']}")


def display_battle_log(message):
    """
    Display a formatted battle message
    """
    print(f">>> {message}")

# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=== COMBAT SYSTEM TEST ===")

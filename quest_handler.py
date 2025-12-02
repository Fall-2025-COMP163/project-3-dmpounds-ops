"""
COMP 163 - Project 3: Quest Chronicles
Quest Handler Module - Starter Code

Name: [Your Name Here]

AI Usage: [Document any AI assistance used]

This module handles quest management, dependencies, and completion.
"""

import character_manager
from custom_exceptions import (
    QuestNotFoundError,
    QuestRequirementsNotMetError,
    QuestAlreadyCompletedError,
    QuestNotActiveError,
    InsufficientLevelError
)

# ============================================================================
# QUEST MANAGEMENT
# ============================================================================

def accept_quest(character, quest_id, quest_data_dict):
    """
    Accept a new quest
    ...
    """
    if quest_id not in quest_data_dict:
        raise QuestNotFoundError(f"Quest {quest_id} not found")

    quest = quest_data_dict[quest_id]

    # Level requirement
    if character.get("level", 1) < quest.get("required_level", 1):
        raise InsufficientLevelError("Level too low for this quest")

    # Prerequisite
    prereq = quest.get("prerequisite", "NONE")
    if prereq != "NONE" and prereq not in character.get("completed_quests", []):
        raise QuestRequirementsNotMetError("Prerequisite quest not completed")

    # Already completed?
    if quest_id in character.get("completed_quests", []):
        raise QuestAlreadyCompletedError("Quest already completed")

    # Already active?
    if quest_id in character.get("active_quests", []):
        return False

    character.setdefault("active_quests", []).append(quest_id)
    return True


def complete_quest(character, quest_id, quest_data_dict):
    """
    Complete an active quest and grant rewards
    ...
    """
    if quest_id not in quest_data_dict:
        raise QuestNotFoundError(f"Quest {quest_id} not found")

    if quest_id not in character.get("active_quests", []):
        raise QuestNotActiveError("Quest is not active")

    quest = quest_data_dict[quest_id]

    # Move from active to completed
    character["active_quests"].remove(quest_id)
    character.setdefault("completed_quests", []).append(quest_id)

    # Grant rewards
    xp = quest.get("reward_xp", 0)
    gold = quest.get("reward_gold", 0)
    character_manager.gain_experience(character, xp)
    character_manager.add_gold(character, gold)

    return {"xp": xp, "gold": gold}


def abandon_quest(character, quest_id):
    """
    Remove a quest from active quests without completing it
    
    Returns: True if abandoned
    Raises: QuestNotActiveError if quest not active
    """
    if quest_id not in character.get("active_quests", []):
        raise QuestNotActiveError("Quest is not active")

    character["active_quests"].remove(quest_id)
    return True


def get_active_quests(character, quest_data_dict):
    """
    Get full data for all active quests
    
    Returns: List of quest dictionaries for active quests
    """
    result = []
    for qid in character.get("active_quests", []):
        if qid in quest_data_dict:
            result.append(quest_data_dict[qid])
    return result


def get_completed_quests(character, quest_data_dict):
    """
    Get full data for all completed quests
    
    Returns: List of quest dictionaries for completed quests
    """
    result = []
    for qid in character.get("completed_quests", []):
        if qid in quest_data_dict:
            result.append(quest_data_dict[qid])
    return result


def get_available_quests(character, quest_data_dict):
    """
    Get quests that character can currently accept
    
    Available = meets level req + prerequisite done + not completed + not active
    
    Returns: List of quest dictionaries
    """
    available = []
    for qid, quest in quest_data_dict.items():
        if can_accept_quest(character, qid, quest_data_dict):
            available.append(quest)
    return available

# ============================================================================
# QUEST TRACKING
# ============================================================================

def is_quest_completed(character, quest_id):
    """
    Check if a specific quest has been completed
    
    Returns: True if completed, False otherwise
    """
    return quest_id in character.get("completed_quests", [])


def is_quest_active(character, quest_id):
    """
    Check if a specific quest is currently active
    
    Returns: True if active, False otherwise
    """
    return quest_id in character.get("active_quests", [])


def can_accept_quest(character, quest_id, quest_data_dict):
    """
    Check if character meets all requirements to accept quest
    
    Returns: True if can accept, False otherwise
    Does NOT raise exceptions - just returns boolean
    """
    if quest_id not in quest_data_dict:
        return False

    quest = quest_data_dict[quest_id]

    if character.get("level", 1) < quest.get("required_level", 1):
        return False

    prereq = quest.get("prerequisite", "NONE")
    if prereq != "NONE" and prereq not in character.get("completed_quests", []):
        return False

    if quest_id in character.get("completed_quests", []):
        return False

    if quest_id in character.get("active_quests", []):
        return False

    return True


def get_quest_prerequisite_chain(quest_id, quest_data_dict):
    """
    Get the full chain of prerequisites for a quest
    ...
    """
    if quest_id not in quest_data_dict:
        raise QuestNotFoundError(f"Quest {quest_id} not found")

    chain = []
    current = quest_id
    while True:
        chain.append(current)
        prereq = quest_data_dict[current].get("prerequisite", "NONE")
        if prereq == "NONE":
            break
        if prereq not in quest_data_dict:
            raise QuestNotFoundError(f"Prerequisite quest {prereq} not found")
        current = prereq

    chain.reverse()  # earliest first
    return chain

# ============================================================================
# QUEST STATISTICS
# ============================================================================

def get_quest_completion_percentage(character, quest_data_dict):
    """
    Calculate what percentage of all quests have been completed
    
    Returns: Float between 0 and 100
    """
    total = len(quest_data_dict)
    if total == 0:
        return 0.0
    completed = len(character.get("completed_quests", []))
    return (completed / total) * 100.0


def get_total_quest_rewards_earned(character, quest_data_dict):
    """
    Calculate total XP and gold earned from completed quests
    
    Returns: Dictionary with 'total_xp' and 'total_gold'
    """
    total_xp = 0
    total_gold = 0
    for qid in character.get("completed_quests", []):
        quest = quest_data_dict.get(qid)
        if quest:
            total_xp += quest.get("reward_xp", 0)
            total_gold += quest.get("reward_gold", 0)
    return {"total_xp": total_xp, "total_gold": total_gold}


def get_quests_by_level(quest_data_dict, min_level, max_level):
    """
    Get all quests within a level range
    
    Returns: List of quest dictionaries
    """
    result = []
    for quest in quest_data_dict.values():
        lvl = quest.get("required_level", 1)
        if min_level <= lvl <= max_level:
            result.append(quest)
    return result

# ============================================================================
# DISPLAY FUNCTIONS
# ============================================================================

def display_quest_info(quest_data):
    """
    Display formatted quest information
    
    Shows: Title, Description, Rewards, Requirements
    """
    print(f"\n=== {quest_data['title']} ===")
    print(f"Description: {quest_data['description']}")
    print(f"Required Level: {quest_data['required_level']}")
    print(f"Rewards: {quest_data['reward_xp']} XP, {quest_data['reward_gold']} gold")
    prereq = quest_data.get("prerequisite", "NONE")
    if prereq != "NONE":
        print(f"Prerequisite: {prereq}")
    else:
        print("Prerequisite: None")


def display_quest_list(quest_list):
    """
    Display a list of quests in summary format
    
    Shows: Title, Required Level, Rewards
    """
    if not quest_list:
        print("No quests to display.")
        return

    for quest in quest_list:
        print(f"- {quest['title']} (Level {quest['required_level']}) "
              f"- {quest['reward_xp']} XP, {quest['reward_gold']} gold")


def display_character_quest_progress(character, quest_data_dict):
    """
    Display character's quest statistics and progress
    """
    active = len(character.get("active_quests", []))
    completed = len(character.get("completed_quests", []))
    total = len(quest_data_dict)
    percent = get_quest_completion_percentage(character, quest_data_dict)
    totals = get_total_quest_rewards_earned(character, quest_data_dict)

    print("\n=== QUEST PROGRESS ===")
    print(f"Active quests: {active}")
    print(f"Completed quests: {completed}/{total} ({percent:.1f}% complete)")
    print(f"Total rewards earned: {totals['total_xp']} XP, {totals['total_gold']} gold")

# ============================================================================
# VALIDATION
# ============================================================================

def validate_quest_prerequisites(quest_data_dict):
    """
    Validate that all quest prerequisites exist
    ...
    """
    for quest in quest_data_dict.values():
        prereq = quest.get("prerequisite", "NONE")
        if prereq != "NONE" and prereq not in quest_data_dict:
            raise QuestNotFoundError(f"Invalid prerequisite quest: {prereq}")
    return True

# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=== QUEST HANDLER TEST ===")

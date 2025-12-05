import json
import os
from pathlib import Path
from services.bot import config
from services.bot.Framework.helpers.logger import LOGGER

WHITELIST_FILE = Path("whitelist.json")

def load_whitelist() -> list[int]:
    """Loads the whitelist from file, initializing with env vars if empty."""
    whitelist = set()

    # Load from file if exists
    if WHITELIST_FILE.exists():
        try:
            with open(WHITELIST_FILE, "r") as f:
                data = json.load(f)
                whitelist.update(data)
        except Exception as e:
            LOGGER.error(f"Error loading whitelist: {e}")

    # Always include env var allowed IDs and Owner
    if config.ALLOWED_USER_IDS:
        whitelist.update(config.ALLOWED_USER_IDS)
    
    if config.OWNER_ID:
        try:
            whitelist.add(int(config.OWNER_ID))
        except ValueError:
            pass

    return list(whitelist)

def save_whitelist(user_ids: list[int]):
    """Saves the whitelist to file."""
    try:
        with open(WHITELIST_FILE, "w") as f:
            json.dump(user_ids, f)
    except Exception as e:
        LOGGER.error(f"Error saving whitelist: {e}")

def add_user(user_id: int) -> bool:
    """Adds a user to the whitelist."""
    current_list = set(load_whitelist())
    if user_id in current_list:
        return False
    
    current_list.add(user_id)
    save_whitelist(list(current_list))
    return True

def remove_user(user_id: int) -> bool:
    """Removes a user from the whitelist."""
    current_list = set(load_whitelist())
    
    # Prevent removing owner
    if config.OWNER_ID and user_id == int(config.OWNER_ID):
        return False

    if user_id not in current_list:
        return False
    
    current_list.remove(user_id)
    save_whitelist(list(current_list))
    return True

def is_user_allowed(user_id: int) -> bool:
    """Checks if a user is allowed."""
    # If no whitelist is configured at all (env var empty and file empty), 
    # we might want to allow everyone OR block everyone. 
    # Current logic: if env var was empty, auth.py allowed everyone.
    # But now we want strict control.
    
    # However, to maintain backward compatibility: 
    # If whitelist.json doesn't exist AND env var is empty, maybe allow all?
    # But the user wants control. So let's assume strict mode if this system is active.
    
    allowed_users = load_whitelist()
    if not allowed_users:
        # If absolutely no one is on the list, maybe allow owner at least?
        # If list is empty, it means no env vars and no file. 
        # For safety, if list is empty, maybe allow all (default behavior) or block all.
        # Let's stick to: if list is NOT empty, enforce it. If empty, allow all (dev mode).
        return True
        
    return user_id in allowed_users

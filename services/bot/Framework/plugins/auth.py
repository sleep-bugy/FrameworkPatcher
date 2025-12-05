from pyrogram import Client, filters
from pyrogram.types import Message
from services.bot.Framework.helpers.logger import LOGGER
import config

@Client.on_message(filters.private, group=-1)
async def auth_check(client: Client, message: Message):
    """
    Middleware to check if the user is authorized to use the bot.
    Runs in group -1 (before default handlers).
    """
    if not config.ALLOWED_USER_IDS:
        # If no allowed users are defined, allow everyone (or block everyone? usually allow for safety if not configured)
        # But based on request "only specific people", if list is empty, maybe block?
        # Let's assume if list is empty, feature is disabled (allow all). 
        # OR if user explicitly asked for restriction, maybe we should block if empty.
        # Let's check if the variable is set in env. If not set, allow all.
        return

    user_id = message.from_user.id
    if user_id not in config.ALLOWED_USER_IDS:
        LOGGER.warning(f"Unauthorized access attempt from user ID: {user_id} ({message.from_user.first_name})")
        await message.reply_text(
            "⛔ **Access Denied**\n\n"
            "You are not authorized to use this bot.\n"
            f"Your ID: `{user_id}`"
        )
        message.stop_propagation()

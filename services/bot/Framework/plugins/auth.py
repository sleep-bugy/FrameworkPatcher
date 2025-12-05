from pyrogram import Client, filters
from pyrogram.types import Message
from services.bot.Framework.helpers.logger import LOGGER
from services.bot.Framework.helpers.whitelist import is_user_allowed

@Client.on_message(filters.private, group=-1)
async def auth_check(client: Client, message: Message):
    """
    Middleware to check if the user is authorized to use the bot.
    Runs in group -1 (before default handlers).
    """
    user_id = message.from_user.id
    
    if is_user_allowed(user_id):
        return

    # If we reach here, user is NOT allowed
    LOGGER.warning(f"Unauthorized access attempt from user ID: {user_id} ({message.from_user.first_name})")
    await message.reply_text(
        "⛔ **Access Denied**\n\n"
        "You are not authorized to use this bot.\n"
        f"Your ID: `{user_id}`"
    )
    message.stop_propagation()


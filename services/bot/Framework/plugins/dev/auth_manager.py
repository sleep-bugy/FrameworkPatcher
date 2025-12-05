from pyrogram import Client, filters
from pyrogram.types import Message
from services.bot.Framework.helpers.decorators import owner
from services.bot.Framework.helpers.whitelist import add_user, remove_user, load_whitelist
from services.bot.Framework.helpers.logger import LOGGER

@Client.on_message(filters.command("add") & filters.private)
@owner
async def add_user_handler(client: Client, message: Message):
    """Adds a user to the whitelist."""
    try:
        if len(message.command) < 2:
            await message.reply_text("Usage: `/add <user_id>`")
            return

        user_id = int(message.command[1])
        if add_user(user_id):
            await message.reply_text(f"✅ User `{user_id}` added to whitelist.")
            LOGGER.info(f"User {user_id} added to whitelist by owner.")
        else:
            await message.reply_text(f"⚠️ User `{user_id}` is already in the whitelist.")

    except ValueError:
        await message.reply_text("❌ Invalid User ID. Please enter a number.")
    except Exception as e:
        LOGGER.error(f"Error adding user: {e}")
        await message.reply_text(f"❌ Error: {e}")

@Client.on_message(filters.command("del") & filters.private)
@owner
async def del_user_handler(client: Client, message: Message):
    """Removes a user from the whitelist."""
    try:
        if len(message.command) < 2:
            await message.reply_text("Usage: `/del <user_id>`")
            return

        user_id = int(message.command[1])
        if remove_user(user_id):
            await message.reply_text(f"✅ User `{user_id}` removed from whitelist.")
            LOGGER.info(f"User {user_id} removed from whitelist by owner.")
        else:
            await message.reply_text(f"⚠️ User `{user_id}` is not in the whitelist (or is the Owner).")

    except ValueError:
        await message.reply_text("❌ Invalid User ID. Please enter a number.")
    except Exception as e:
        LOGGER.error(f"Error removing user: {e}")
        await message.reply_text(f"❌ Error: {e}")

@Client.on_message(filters.command("users") & filters.private)
@owner
async def list_users_handler(client: Client, message: Message):
    """Lists all authorized users."""
    users = load_whitelist()
    if not users:
        await message.reply_text("📝 Whitelist is empty (Public Access).")
        return

    text = "📝 **Authorized Users:**\n\n"
    for uid in users:
        text += f"• `{uid}`\n"
    
    await message.reply_text(text)

@Client.on_message(filters.command("broadcast") & filters.private)
@owner
async def broadcast_handler(client: Client, message: Message):
    """Broadcasts a message to all authorized users."""
    if len(message.command) < 2 and not message.reply_to_message:
        await message.reply_text("Usage: `/broadcast <message>` or reply to a message.")
        return

    users = load_whitelist()
    sent_count = 0
    failed_count = 0

    msg_text = message.text.split(None, 1)[1] if len(message.command) > 1 else None
    
    status_msg = await message.reply_text("📢 Broadcasting...")

    for uid in users:
        if uid == message.from_user.id:
            continue
            
        try:
            if message.reply_to_message:
                await message.reply_to_message.copy(uid)
            else:
                await client.send_message(uid, msg_text)
            sent_count += 1
        except Exception:
            failed_count += 1
    
    await status_msg.edit_text(
        f"✅ **Broadcast Complete**\n\n"
        f"Sent: {sent_count}\n"
        f"Failed: {failed_count}"
    )

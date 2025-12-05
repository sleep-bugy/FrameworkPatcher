from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from services.bot.Framework import bot
from services.bot.Framework.helpers.state import *


@bot.on_callback_query(filters.regex(r"^start_patch_cb$"))
async def start_patch_callback(bot: Client, query: CallbackQuery):
    """Handles the start patching button callback."""
    await start_patch_command(bot, query.message)
    await query.answer()


@bot.on_message(filters.private & filters.command("start_patch"))
async def start_patch_command(bot: Client, message: Message):
    """Initiates the framework patching conversation."""
    user_id = message.from_user.id
    # Initialize state and prompt for device codename
    user_states[user_id] = {
        "state": STATE_WAITING_FOR_DEVICE_CODENAME,
        "files": {},
        "device_name": None,
        "device_codename": None,
        "version_name": None,
        "android_version": None,
        "api_level": None,
        "codename_retry_count": 0,
        "software_data": None,
        "features": {
            "enable_signature_bypass": False,
            "enable_cn_notification_fix": False,
            "enable_disable_secure_flag": False,
            "enable_kaorios_toolbox": False
        }
    }
    
    text = (
        "🚀 **Let's start patching!**\n\n"
        "First, I need to know your device details.\n\n"
        "📱 **Please enter your device codename**\n"
        "Examples: `rothko`, `xaga`, `marble`, `mondrian`\n\n"
        "💡 _Tip: If you don't know the codename, you can type the device name (e.g., 'Redmi Note 12 Turbo')._"
    )
    
    if isinstance(message, Message):
        await message.reply_text(text, quote=True)
    else:
        await message.edit_text(text)


@bot.on_callback_query(filters.regex(r"^reselect_codename$"))
async def reselect_codename_handler(bot: Client, query: CallbackQuery):
    """Handles reselecting device codename."""
    user_id = query.from_user.id
    if user_id not in user_states:
        await query.answer("Session expired. Use /start_patch to begin.", show_alert=True)
        return

    # Reset to codename selection state
    user_states[user_id]["state"] = STATE_WAITING_FOR_DEVICE_CODENAME
    user_states[user_id]["device_codename"] = None
    user_states[user_id]["device_name"] = None
    user_states[user_id]["software_data"] = None
    user_states[user_id]["codename_retry_count"] = 0
    
    await query.message.edit_text(
        "📱 Please enter your device codename (e.g., rothko, xaga, marble)\n\n"
        "💡 Tip: You can also search by device name if you don't know the codename."
    )
    await query.answer("Codename reset. Enter a new codename.")


@bot.on_callback_query(filters.regex(r"^feature_(signature|cn_notif|secure_flag|kaorios)$"))
async def feature_toggle_handler(bot: Client, query: CallbackQuery):
    """Handles toggling features on/off."""
    user_id = query.from_user.id
    if user_id not in user_states or user_states[user_id].get("state") != STATE_WAITING_FOR_FEATURES:
        await query.answer("Not expecting feature selection.", show_alert=True)
        return
    
    feature_map = {
        "feature_signature": "enable_signature_bypass",
        "feature_cn_notif": "enable_cn_notification_fix",
        "feature_secure_flag": "enable_disable_secure_flag",
        "feature_kaorios": "enable_kaorios_toolbox"
    }
    
    feature_key = feature_map.get(query.data)
    if feature_key:
        # Toggle feature
        user_states[user_id]["features"][feature_key] = not user_states[user_id]["features"][feature_key]
    
    # Update button display
    features = user_states[user_id]["features"]
    android_version = user_states[user_id].get("android_version", "15")
    android_int = int(float(android_version))

    buttons = [
        [InlineKeyboardButton(
            f"{'✅' if features['enable_signature_bypass'] else '❌'} Signature Verification Bypass",
            callback_data="feature_signature"
        )]
    ]

    # Only show Android 15+ features if Android version is 15 or higher
    if android_int >= 15:
        buttons.append([InlineKeyboardButton(
            f"{'✅' if features['enable_cn_notification_fix'] else '❌'} CN Notification Fix",
            callback_data="feature_cn_notif"
        )])
        buttons.append([InlineKeyboardButton(
            f"{'✅' if features['enable_disable_secure_flag'] else '❌'} Disable Secure Flag",
            callback_data="feature_secure_flag"
        )])
        buttons.append([InlineKeyboardButton(
            f"{'✅' if features['enable_kaorios_toolbox'] else '❌'} Kaorios Toolbox",
            callback_data="feature_kaorios"
        )])

    buttons.append([InlineKeyboardButton("🚀 Continue with selected features", callback_data="features_done")])

    await query.message.edit_reply_markup(InlineKeyboardMarkup(buttons))
    await query.answer(f"Feature {'enabled' if user_states[user_id]['features'][feature_key] else 'disabled'}")


@bot.on_callback_query(filters.regex(r"^features_done$"))
async def features_done_handler(bot: Client, query: CallbackQuery):
    """Handles when user is done selecting features."""
    user_id = query.from_user.id
    if user_id not in user_states or user_states[user_id].get("state") != STATE_WAITING_FOR_FEATURES:
        await query.answer("Not expecting feature confirmation.", show_alert=True)
        return
    
    features = user_states[user_id]["features"]
    
    # Check if at least one feature is selected
    if not any(features.values()):
        await query.answer("⚠ Please select at least one feature!", show_alert=True)
        return
    
    # Build features summary
    selected_features = []
    if features["enable_signature_bypass"]:
        selected_features.append("✓ Signature Verification Bypass")
    if features["enable_cn_notification_fix"]:
        selected_features.append("✓ CN Notification Fix")
    if features["enable_disable_secure_flag"]:
        selected_features.append("✓ Disable Secure Flag")
    if features["enable_kaorios_toolbox"]:
        selected_features.append("✓ Kaorios Toolbox (Play Integrity Fix)")
    
    features_text = "\n".join(selected_features)
    
    user_states[user_id]["state"] = STATE_WAITING_FOR_FILES
    await query.message.edit_text(
        f"✅ Features selected:\n\n{features_text}\n\n"
        "Now, please send all 3 JAR files:\n"
        "• framework.jar\n"
        "• services.jar\n"
        "• miui-services.jar"
    )
    await query.answer("Features confirmed!")

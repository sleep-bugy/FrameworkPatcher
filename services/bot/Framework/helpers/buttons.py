from pyrogram.types import InlineKeyboardButton



START_TEXT = """👋 **Hello {}, Welcome to Framework Patcher Bot!**

I can help you patch your **HyperOS/MIUI** framework files to unlock cool features.

🚀 **Features Supported:**
• **Signature Verification Bypass** (Install unsigned apps)
• **CN Notification Fix** (Fix notifications on CN ROMs)
• **Disable Secure Flag** (Allow screenshots in secure apps)
• **Kaorios Toolbox** (Play Integrity & Google Photos Unlimited)

🤖 **Supported Android Versions:**
• Android 13 - 16

👇 **Click the button below or type** `/start_patch` **to begin!**"""

BUTTON1 = InlineKeyboardButton(text="👨‍💻 Developer", url="https://t.me/manusiatukangtidur")
BUTTON2 = InlineKeyboardButton(text="👥 Support Group", url="https://t.me/SleepDiscussion")
BUTTON_SUPPORT = InlineKeyboardButton(text="☕ Support me", url="https://graph.org/Developer-Support-with-Coffee-05-19")
BUTTON_START_PATCH = InlineKeyboardButton(text="🚀 Start Patching", callback_data="start_patch_cb")

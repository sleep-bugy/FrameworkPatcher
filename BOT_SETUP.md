# Telegram Bot Setup Guide

This guide will help you create a Telegram bot and set it up for the Framework Patcher project.

## 1. Create a New Bot

1.  Open Telegram and search for **@BotFather**.
2.  Start a chat and send the command `/newbot`.
3.  Follow the instructions:
    *   **Name**: Choose a display name for your bot (e.g., "My Framework Patcher").
    *   **Username**: Choose a unique username ending in `bot` (e.g., `MyPatcherBot`).
4.  Once created, BotFather will give you an **API Token**.
    *   Example: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`
    *   **Keep this token secret!**

## 2. Get Your ID (Optional but Recommended)

To restrict the bot so only you can use it (or to know your ID for config), you need your Telegram User ID.

1.  Search for **@userinfobot** on Telegram.
2.  Start the chat.
3.  It will reply with your **Id**. Copy this number.

## 3. Configure the Project

1.  Navigate to the `services/bot` directory in the project.
2.  Create a `.env` file (if it doesn't exist) or edit the existing one.
3.  Add your bot token and other configurations:

```env
# Telegram Bot Token from BotFather
BOT_TOKEN=your_api_token_here

# Your Telegram User ID (for admin permissions if needed)
OWNER_ID=your_user_id_here

# GitHub Configuration (for the patcher workflow)
GITHUB_TOKEN=your_github_personal_access_token
GITHUB_REPO=your_username/FrameworkPatcher
```

## 4. Run the Bot

You can run the bot using Python:

```bash
cd services/bot
python3 -m Framework
```

Or if there is a deploy script:

```bash
./deploy.sh
```

## 5. Customizing the Bot (Optional)

You can set the bot's profile picture, description, and commands using @BotFather:
*   `/setuserpic` - Change bot's profile photo.
*   `/setdescription` - Change the text shown before user starts the bot.
*   `/setcommands` - Set the command list menu.

Recommended commands:
```
start - Start the bot
start_patch - Start patching process
cancel - Cancel current operation
ping - Check bot status
```

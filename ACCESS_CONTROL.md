# Access Control Setup Guide

This guide explains how to restrict access to your Framework Patcher Bot and Web Interface.

## 1. Configure Environment Variables

You need to update your `.env` file in `services/bot/.env` (or wherever you store your secrets) with the following variables:

```env
# --- Access Control Configuration ---

# 1. Telegram Bot Whitelist
# Comma-separated list of Telegram User IDs allowed to use the bot.
# You can get your ID from @userinfobot on Telegram.
ALLOWED_USER_IDS=123456789,987654321

# 2. Web Interface Access Code
# A secret password required to access the web interface.
WEB_ACCESS_CODE=secret_password_here
```

## 2. How it Works

### Telegram Bot
*   Only users whose ID is in `ALLOWED_USER_IDS` can interact with the bot.
*   Unauthorized users will receive an "Access Denied" message.
*   If `ALLOWED_USER_IDS` is empty or not set, the bot might allow everyone (depending on implementation safety), so **make sure to set it!**

### Web Interface
*   When opening the web page, a **Login Modal** will appear.
*   You must enter the `WEB_ACCESS_CODE` to unlock the interface.
*   The code is verified by the server.
*   Once unlocked, the code is saved in your browser so you don't have to enter it every time (until you clear cache).

# Deployment Guide

This guide explains how to deploy the Framework Patcher.

## Architecture Overview

The project consists of two separate parts that need to be run differently:

1.  **Web Interface (`services/web`)**: A website + API.
    *   **Where to run:** Vercel (Recommended) or any VPS.
    *   **Database:** None required (uses GitHub API and in-memory cache).
2.  **Telegram Bot (`services/bot`)**: A background process.
    *   **Where to run:** VPS (Virtual Private Server), Local PC, or a container host (Railway/Heroku).
    *   **Cannot run on Vercel** because it needs to run continuously (Long Polling).

---

## Part 1: Deploying the Web Interface (Vercel)

We have configured the project to be easily deployed on Vercel.

### Prerequisites
*   A [Vercel Account](https://vercel.com).
*   GitHub repository with this code.

### Steps
1.  Go to your Vercel Dashboard and click **"Add New..."** -> **"Project"**.
2.  Import your GitHub repository.
3.  **Configure Project:**
    *   **Framework Preset:** Other (or leave default).
    *   **Root Directory:** `./` (Root of the repo).
4.  **Environment Variables:**
    Add the following variables in the Vercel Project Settings:
    *   `GITHUB_TOKEN`: Your GitHub Personal Access Token.
    *   `GITHUB_OWNER`: Your GitHub Username.
    *   `GITHUB_REPO`: This repository name.
    *   `WORKFLOW_ID`: Default workflow ID.
    *   `WEB_ACCESS_CODE`: The password for the website.
    *   *(Add other workflow IDs as needed: `GITHUB_WORKFLOW_ID_A13`, etc.)*
5.  Click **Deploy**.

Vercel will automatically detect the configuration in `vercel.json` and `services/web/requirements.txt` and deploy both the frontend and the backend API.

---

## Part 2: Running the Telegram Bot (VPS)

The bot needs to run on a server that stays online 24/7.

### Prerequisites
*   A Linux VPS (Ubuntu/Debian recommended).
*   Python 3.8 or higher installed.

### Steps

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
    cd FrameworkPatcher
    ```

2.  **Install Dependencies:**
    ```bash
    pip3 install -r services/bot/requirements.txt
    ```

3.  **Configure Environment:**
    Create a `.env` file in `services/bot/.env` (or export variables in your shell):
    ```bash
    cp services/bot/.env.example services/bot/.env
    nano services/bot/.env
    ```
    Fill in:
    *   `API_ID`, `API_HASH` (from my.telegram.org)
    *   `BOT_TOKEN` (from @BotFather)
    *   `ALLOWED_USER_IDS` (Your Telegram ID)

4.  **Run the Bot:**
    *   **Method A: Direct (for testing)**
        ```bash
        python3 -m services.bot.Framework
        ```
        *Note: Run this from the root `FrameworkPatcher` directory.*

    *   **Method B: Systemd Service (Recommended for 24/7)**
        Create a service file:
        ```bash
        sudo nano /etc/systemd/system/frameworkbot.service
        ```
        Content:
        ```ini
        [Unit]
        Description=Framework Patcher Bot
        After=network.target

        [Service]
        User=root
        WorkingDirectory=/path/to/FrameworkPatcher
        ExecStart=/usr/bin/python3 -m services.bot.Framework
        Restart=always

        [Install]
        WantedBy=multi-user.target
        ```
        Enable and start:
        ```bash
        sudo systemctl enable frameworkbot
        sudo systemctl start frameworkbot
        ```

---

## FAQ

**Q: Do I need a database?**
A: **No.** The project uses GitHub as a backend storage (for downloading files) and in-memory caching for the device list. No SQL/Mongo database is required.

**Q: Can I run the bot on Vercel?**
A: No. Vercel is for websites and short-lived functions. Telegram bots need to stay connected to Telegram servers continuously, which Vercel kills after a few seconds.

**Q: Where do I run the Python commands?**
A:
*   **For Web:** You don't need to run commands manually if using Vercel. Vercel runs them for you.
*   **For Bot:** You run them in the terminal (SSH) of your VPS.

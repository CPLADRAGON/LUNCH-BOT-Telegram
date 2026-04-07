# 🍱 Singapore Lunch Bot

A simple, automated Telegram bot for team lunch coordination.

## ✨ Features

- **🇸🇬 Singapore Holiday Aware**: Skips weekends and official SG Public Holidays.
- **⛈️ Targeted Weather Alert**: Checks the forecast for **Kallang (8 Kallang Sector)** at **11:15 AM SGT**.
- **🗳️ Interactive Polls**: Sends a native poll at **11:00 AM SGT**.
- **🔔 Smart Reminders**: Mentions people who haven't voted by **11:20 AM SGT**.
- **🏆 Monthly Leaderboard**: Keeps track of lunch attendance and summarizes at month-end.

## 🛠️ Setup Instructions

### 1. Create your Telegram Bot
1. Message [@BotFather](https://t.me/botfather) on Telegram.
2. Send `/newbot` and follow the instructions to get your **Bot Token**.
3. Add your new bot to your group chat.

### 2. Get your Group Chat ID
1. Add `@myidbot` to your group chat.
2. Type `/getgroupid` in the group.
3. Copy the ID (it should start with a minus sign, e.g., `-100123456789`).

### 3. Configure GitHub Secrets
In your GitHub repository:
1. Go to **Settings** > **Secrets and variables** > **Actions**.
2. Click **New repository secret** and add:
   - `TELEGRAM_BOT_TOKEN`: Your token from Step 1.
   - `TELEGRAM_CHAT_ID`: Your group ID from Step 2.
   - `REGULARS`: (Optional) A comma-separated list of usernames to remind at 11:20 am (e.g. `alice, bob, charlie`).
   
## 📊 How to "Call" the Leaderboard
Since this bot runs on a schedule, you can't type `/leaderboard` in the chat. Instead:
1. Go to your GitHub repository.
2. Click on the **Actions** tab.
3. Select **Daily Lunch Poll Bot** on the left.
4. Click the **Run workflow** button.
5. The bot will immediately post the latest standings to your Telegram group!

---
*Created with ❤️ for hungry teams in Kallang.*

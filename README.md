# 🍱 Singapore Lunch Bot

A simple, automated Telegram bot that asks your group chat "Who's coming for lunch?" every working day at **11:00 AM Singapore Time**.

## ✨ Features

- **🇸🇬 Singapore Holiday Aware**: Automatically skips weekends and all official Singapore Public Holidays.
- **☁️ 100% Free Hosting**: Runs on GitHub Actions—no server or payment required.
- **🗳️ Interactive Polls**: Sends a native Telegram poll so you can see who's joining at a glance.
- **🚀 Set and Forget**: Once configured, it runs automatically every weekday.

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

## 📂 Project Structure

- `lunch_bot.py`: The main logic script (Python).
- `.github/workflows/daily_lunch_poll.yml`: The automation schedule (11:00 AM SGT).
- `requirements.txt`: Necessary Python libraries (`requests`, `holidays`).

## 🧪 Local Testing

If you want to test the script locally:

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set your environment variables:
   ```bash
   export TELEGRAM_BOT_TOKEN='your_token'
   export TELEGRAM_CHAT_ID='your_id'
   ```

3. Run the script:
   ```bash
   python lunch_bot.py
   ```

---
*Created with ❤️ for hungry teams in Singapore.*

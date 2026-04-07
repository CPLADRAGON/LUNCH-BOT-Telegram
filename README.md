# 🍱 Singapore Lunch Bot (Real-Time Edition)

A premium, automated Telegram bot for team lunch coordination, now upgraded with real-time interactivity and hyper-local SG weather data.

## ✨ Features

- **🇸🇬 Singapore Holiday Aware**: Skips weekends and official SG Public Holidays.
- **🌦️ Daily Lunch Briefing**: Checks the forecast for **Kallang (8 Kallang Sector)**, **UV Index**, and **"Feels Like" Temperature** at **11:15 AM SGT**.
- **🗳️ Interactive Polls**: Sends a native poll at **11:00 AM SGT**.
- **👑 Social Leaderboard**: Earn titles like **"Kallang Loyal" (3+ days)** or **"Lunch King" (5+ days)** based on your attendance!
- **⚡ Real-Time Commands**: Now responds instantly to `/weather` and `/leaderboard` via Vercel Webhooks.
- **🔔 Smart Reminders**: Mentions people who haven't voted by **11:20 AM SGT**.

## 🛠️ Setup Instructions

### 1. Telegram & Database Setup
1. Create a bot with [@BotFather](https://t.me/botfather) to get your **Bot Token**.
2. Add your bot to your group and get the **Chat ID** (starting with `-100`).
3. Create a free **Upstash Redis** database to store the leaderboard data.

### 2. Deployment (Vercel + GitHub)
The bot uses a hybrid architecture:
- **GitHub Actions**: Handles the daily schedule (Poll, Briefing, Reminders).
- **Vercel**: Handles real-time commands (`/weather`, `/leaderboard`).

#### Configure Environment Variables
Set these in **both** GitHub Secrets and Vercel Environment Variables:
- `TELEGRAM_BOT_TOKEN`: Your Bot Token.
- `TELEGRAM_CHAT_ID`: Your Group Chat ID.
- `UPSTASH_REDIS_REST_URL`: Provided by Upstash.
- `UPSTASH_REDIS_REST_TOKEN`: Provided by Upstash.
- `REGULARS`: (Optional) Comma-separated list of usernames (e.g. `alice,bob`).

### 3. Set the Webhook
Once deployed on Vercel, link your bot to the new URL:
`https://api.telegram.org/bot<TOKEN>/setWebhook?url=https://<YOUR_VERCEL_URL>/`

## 📊 Commands
- `/weather`: Get a real-time lunch briefing (Forecast, UV, and Heat Index).
- `/leaderboard`: See who's leading the lunch pack and their earned titles.

---
*Created with ❤️ for hungry teams in Kallang. Upgraded with Real-Time Interactivity.*

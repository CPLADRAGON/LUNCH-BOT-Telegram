# 🍱 Singapore Lunch Bot (AI Hype Edition) 🚀

![Lunch Bot Mascot](./assets/mascot.png)

> **"No more lunch guessing games. Powered by Gemini 3.1, built for high-performance lunch coordination."**

A premium, automated Telegram bot for team lunch coordination. Now upgraded to a **100% Serverless Architecture** with Upstash QStash, Gemini 3.1 Flash-Lite AI, and hyper-local Singapore weather data.

## 🏗️ Modern Architecture
The bot has transitioned from brittle GitHub Actions to a production-grade serverless stack:
- **Compute**: Vercel Serverless Functions.
- **Scheduler**: Upstash QStash (High-precision cron).
- **Intelligence**: Gemini 3.1 Flash-Lite (via `google-genai`).
- **Persistence**: Upstash Redis.

## ✨ Core Features

### 🤖 AI Hype-Bot
- **Gemini 3.1 Powered**: High-speed, energetic motivation for the team.
- **Interactive Chat**: Responds instantly to `@mentions` and provides private 1-on-1 hype.
- **Scheduled Motivation**: Morning motivational blasts to kick off the day.

### 📅 Precision Coordination
- **🇸🇬 Holiday Aware**: Skips weekends and SG Public Holidays automatically.
- **🌦️ Weather Briefing**: Real-time forecast for **Kallang sector**, UV Index, and Heat Index.
- **🗳️ Native Polls**: Automated coordination at 11:00 AM sharp.
- **📣 AI Leaderboard Cheer**: Personalized, celebratory standinds at 12:30 PM.
- **🔔 Smart Reminders**: Automatically nudges non-voters.

## ⏰ Daily Routine (SGT)
The bot follows a strict schedule via **Upstash QStash**:
- **10:45 AM**: ⚡ AI Hype Message
- **11:00 AM**: 🍱 Daily Lunch Poll
- **11:15 AM**: ⛅ Weather & UV Briefing
- **11:20 AM**: 📢 Voter Reminder
- **12:30 PM**: 🏆 AI Leaderboard Cheer (Dynamic Standings)
- **12:00 PM (Last Working Day)**: 🏅 Monthly Reset & Crown Ceremony

## 🛠️ Setup Instructions

### 1. Deployment
1. **Vercel**: Link your repository to Vercel.
2. **Upstash**: Set up a **Redis** instance and a **QStash** schedule pointing to your Vercel URL.
   - URL Format: `https://your-app.vercel.app/api/cron?mode=MODE&secret=YOUR_SECRET`

### 2. Environment Variables
Configure these in **Vercel**:
- `TELEGRAM_BOT_TOKEN`: Your API token from @BotFather.
- `TELEGRAM_CHAT_ID`: The target group ID (Starts with `-100...`).
- `CRON_SECRET`: A secure key used to authorize QStash calls.
- `GEMINI_API_KEY`: Google AI Studio workspace key.
- `UPSTASH_REDIS_REST_URL` / `TOKEN`: Your database credentials.
- `REGULARS`: Comma-separated usernames for the smart reminder system.

---
*Created with ❤️ for hungry teams in Singapore. Powered by Gemini 3.1 Intelligence.*

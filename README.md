# 🍱 Singapore Lunch Bot (AI Hype Edition) 🚀

![Lunch Bot Mascot](./assets/mascot.png)

> **"No more lunch guessing games. Powered by Gemini 3.1, built for Kallang lunch people."**

A premium, automated Telegram bot for team lunch coordination. Now upgraded with **Gemini 3.1 Flash-Lite AI**, hyper-local Singapore weather data, and 100% reliable automated scheduling.

## 📽️ Project Presentation
We've prepared a professional overview of the bot's features and architecture:
👉 **[Download LunchBot_Deck.pptx](./LunchBot_Deck.pptx)**

## ✨ Core Features

### 🤖 AI Hype-Bot (New!)
- **Gemini 3.1 Powered**: Uses the latest `google-genai` SDK for high-speed, energetic motivation.
- **Interactive Chat**: Responds to `@mentions` in group chats and provides 24/7 one-on-one hype in private DMs.
- **Scheduled Motivation**: Automatically blasts a "Makan Time" hype message every morning.

### 📅 Precision Scheduling
- **🇸🇬 Holiday Aware**: Skips weekends and official SG Public Holidays.
- **🌦️ Weather Briefing**: Real-time forecast for **Kallang sector**, UV Index, and Heat Index.
- **🗳️ Native Polls**: Automated coordination at 11:00 AM sharp.
- **👑 Social Leaderboard**: Gamified titles like **"Kallang Loyal"** or **"Lunch King"**.
- **🔔 Smart Reminders**: Nudges non-voters automatically.

## ⏰ Daily Routine (SGT)
The bot follows a strict, reliable schedule via GitHub Actions:
- **10:45 AM**: ⚡ AI Hype Message
- **11:00 AM**: 🍱 Daily Lunch Poll
- **11:15 AM**: ⛅ Weather & UV Briefing
- **11:20 AM**: 📢 Voter Reminder
- **12:00 PM**: 🏆 Monthly Leaderboard Reset (Last working day only)

## 🛠️ Setup Instructions

### 1. API Keys & Database
1. **Telegram**: Create a bot via [@BotFather](https://t.me/botfather).
2. **Gemini**: Get an API key from [Google AI Studio](https://aistudio.google.com/).
3. **Database**: Create a free **Upstash Redis** instance.

### 2. Deployment (Hybrid Architecture)
- **GitHub Actions**: Runs the scheduled tasks using explicit mode flags for maximum reliability.
- **Vercel**: Hosts the webhook for instant command responses and AI chat.

#### Environment Variables
Configure these in **both** GitHub Secrets and Vercel:
- `TELEGRAM_BOT_TOKEN`: Your Bot Token.
- `TELEGRAM_CHAT_ID`: Your Group Chat ID.
- `GEMINI_API_KEY`: Your Google AI SDK key.
- `BOT_USERNAME`: Your bot's handle (e.g., `@Lunch_bot`).
- `UPSTASH_REDIS_REST_URL` / `TOKEN`: Redis credentials.
- `REGULARS`: Comma-separated usernames for reminders.

## 📊 Commands
- `/weather`: Get a real-time lunch briefing (Forecast, UV, and Heat Index).
- `/leaderboard`: See the current lunch pack standings.
- `/hype`: Get an instant burst of motivation from the AI.

---
*Created with ❤️ for hungry teams in Kallang. Upgraded with Gemini 3.1 Intelligence.*

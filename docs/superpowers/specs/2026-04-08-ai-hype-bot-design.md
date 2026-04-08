# Spec: AI-Powered "Hype-Bot" Upgrade 🍱⚡

## Goal
Transform the Lunch Bot into an interactive "Energetic Hype-Bot" using Gemini 3.1 Flash Lite. The bot will provide scheduled daily motivation, on-demand hype, and interactive chat capabilities when mentioned.

## 1. AI Persona: The Energetic Hype-Bot
The bot will use a persistent system instruction to define its personality:
- **Tone**: Hyper-energetic, supportive, and enthusiastic.
- **Style**: Emoji-heavy, uses capitalization for emphasis, and maintains a "foodie" obsession.
- **Context**: Aware of its location in Kallang, Singapore. It should frequently reference local food culture (e.g., "Makan time!", "Kallang feast mode").

## 2. Core Features

### A. Scheduled "Morning Hype" (10:30 AM SGT)
- **Trigger**: New GitHub Action workflow at 02:30 UTC (10:30 AM SGT).
- **Logic**: Calls Gemini with a context-aware prompt to generate a "Daily Breakfast/Lunch Hype" message.
- **Example**: "RISE AND SHINE KALLANG! 🚀 The sun is out and the Nasi Lemak is calling your name! Let's crush this morning so we can FEAST at 12! 🔥🍱"

### B. On-Demand Hype (`/hype` command)
- **Trigger**: Telegram command `/hype`.
- **Logic**: Immediately generates and sends a random burst of motivation.

### C. Interactive AI Chat
- **Logic**: The bot responds to free-form text differently based on the chat type:
  - **Group Chats**: Responds only when the bot is `@mentioned` (e.g., `@LunchBot ...`).
  - **Private Chats (DMs)**: Responds to **every message** automatically without needing a mention.
- **Example**: 
  - User: "Where should I go for some good Laksa?"
  - Bot: "OH MY GOSH LAKSA!! 🍜🔥 You absolute legend! You've GOT to hit up the spot in Kallang Sector 1—it's creamy, it's spicy, it's PARADISE!! 🚀🚀"

## 3. Technical Implementation

### Dependencies
- Add `google-generativeai` to `requirements.txt`.

### Secrets & Config
- **`GEMINI_API_KEY`**: New environment variable required in Vercel and GitHub Secrets.
- **Model**: `gemini-3.1-flash-lite`.

### New Files/Modified Files
- **`lunch_bot.py`**: 
  - Implementation of `get_ai_response(prompt)` helper.
  - Implementation of `send_hype()` function.
- **`api/index.py`**:
  - Update webhook handler to process mentions and `/hype` command.
- **`.github/workflows/daily_hype.yml`**:
  - New CRON job for the 10:30 AM SGT trigger.

## 4. Success Criteria
- Bot successfully sends a message at 10:30 AM SGT daily.
- `/hype` command returns a unique, high-energy response.
- Mentioning the bot results in a conversational response that maintains the "Hype-Bot" persona.

---
*Created on: 2026-04-08*

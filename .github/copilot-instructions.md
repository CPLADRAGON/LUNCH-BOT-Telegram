# Copilot Instructions for Singapore Lunch Bot 🍱🚀

This repository contains the **Singapore Lunch Bot (AI Hype Edition)**, a premium Telegram bot for team lunch coordination. It is built as a 100% serverless application deployed on Vercel, scheduled by Upstash QStash, backed by Upstash Redis, and powered by Gemini 3.1 Flash-Lite.

---

## 🛠️ Build, Test, and Lint Commands

There are no compilation or build steps as this is a standard Python serverless codebase.

### Running Tests
Unit and integration tests are written using standard Python logic (without additional test frameworks like `pytest`). Run each test script directly with `python`:

* **Run all tests:**
  ```bash
  python test_bot.py
  python tests/test_monthly_reset.py
  python tests/test_ai_logic.py
  python tests/test_onboarding.py
  ```

* **Run individual test scripts:**
  * **AI Logic / Mocking:** Tests the Gemini client integration and mock hype message generation.
    ```bash
    python tests/test_ai_logic.py
    ```
  * **Holiday Check Logic:** Verifies weekend and Singapore public holiday detection.
    ```bash
    python test_bot.py
    ```
  * **Monthly Reset logic:** Tests last-working-day-of-month logic for April/May 2026.
    ```bash
    python tests/test_monthly_reset.py
    ```
  * **Onboarding & Webhook Flow:** Tests the dynamic onboarding/offboarding, Redis operations, and mock Slack/Telegram webhook event handlers.
    ```bash
    python tests/test_onboarding.py
    ```

---

## 🏗️ High-Level Architecture

The project is structured into three main operational components:

```
LUNCH-BOT-Telegram/
├── api/
│   └── index.py        # Webhook entry point (Vercel Serverless Function)
├── lunch_bot.py        # Core operational library
└── tests/              # Verification & mock suites
```

### 1. The Webhook Handler (`api/index.py`)
- Exposes a Flask app running as a Vercel Serverless Function (mapped via `vercel.json`).
- **`POST /`**: Receives webhooks from the Telegram Bot API. Handles:
  - Standard commands (`/weather`, `/leaderboard`, `/missing`, `/hype`, direct @mentions, and private 1-on-1 chats).
  - Dynamic user management commands (`/join`, `/leave`, `/onboard`, and `/offboard`).
  - Automated member events (`new_chat_members` to auto-add users and `left_chat_member` to auto-remove users).
  - `poll_answer` events (recording active participation).
- **`POST /api/cron?mode=MODE&secret=SECRET`**: Entrypoint for **Upstash QStash** cron triggers. Authorized via `CRON_SECRET` in the `Authorization` header or query string.
- Immediately halts execution if Singapore is on a weekend or public holiday (`lunch_bot.is_working_day()`).

### 2. The Core Logic (`lunch_bot.py`)
- Handles weather fetching, AI hype generation, holiday checks, and Redis operations.
- **Holiday & Tz Logic:** All operations are anchored around SGT (`Asia/Singapore`). Uses the `holidays` library configured with country `'SG'`.
- **Weather Fetcher:** Concurrently requests data from `api.data.gov.sg` v1 environment endpoints (Forecast, UV Index, Temp, Humidity) inside a `ThreadPoolExecutor` to optimize latency and minimize serverless compute time. Calculates an approximate Heat Index ("Feels Like") temperature.
- **Persistence Store:** Tracks daily votes and month-to-date standings using Upstash Redis.
- **AI Integration:** Uses Gemini 3.1 Flash-Lite (`gemini-3.1-flash-lite`) via `google-genai` package to generate custom motivational texts and tally announcements.

### 3. Upstash Redis Schema
- **Daily Votes Tracker:** Stored in a Redis Set under `voted_today:<YYYY-MM-DD>`. Features a 24-hour expiration (`TTL: 86400`) to auto-clean state. Used to compute `/missing` voters.
- **Standings Leaderboard:** Stored in a Redis Hash under `lunch_leaderboard` mapping `username` (lowercase string) to `count` (integer).
- **Regulars List:** Stored in a Redis Set under `regulars` containing lowercase usernames of team members checked for voting. Offers automated self-migration from the static `REGULARS` environment variable if not already existing.

---

## 🔑 Key Conventions & Guidelines

When modifying this repository, strictly adhere to the following rules:

### 1. Singapore Time Zone (SGT)
* Always use `pytz.timezone('Asia/Singapore')` to get the current date and time. Standard `datetime.now()` without a timezone will reference server local time (usually UTC), breaking holiday checks and cron execution windows.

### 2. Telegram Username Storage (Case-Insensitive Standings)
* **Always lower-case Telegram usernames** before recording daily votes or incrementing leaderboard scores in Redis (e.g. `username.lower()`). This ensures consistency across different clients or Telegram client behaviors.

### 3. Serverless Optimization & Latency
* **Connection Pooling:** Use the persistent global `requests.Session()` object (`session`) for HTTP requests rather than executing isolated `requests.get/post` calls. This enables connection reuse and reduces HTTP handshake overhead in serverless containers.
* **Concurrent I/O:** Any multi-resource API fetching (like weather data) must use `ThreadPoolExecutor` to avoid blocking synchronous routes.

### 4. AI Hype Persona Rules
* When modifying prompt structures or system instructions:
  * Maintain the hyper-energetic, supportive, foodie-obsessed persona.
  * Must focus contextually on Singapore, particularly Kallang food culture (referencing *makan*, *hawker centers*, *laksa*, *chicken rice*).
  * Responses must be kept strictly **under 50 words** to avoid telegram message bloat and optimize Gemini token usage.

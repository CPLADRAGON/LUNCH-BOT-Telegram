# Spec: Singapore Lunch Bot Superpowers 🍱🚀

## Goal
Enhance the Singapore Lunch Bot with "Daily Lunch Briefing" (Weather + UV + Heat) and "Custom Titles" (Social Leaderboard) to increase engagement and utility for the team at 8 Kallang Sector.

## 1. Feature: The "Daily Lunch Briefing"
Upgrade the 11:15 AM weather alert into a comprehensive briefing.

### Data Sources (Data.gov.sg v2 APIs)
- **Forecast**: `https://api-open.data.gov.sg/v2/real-time/api/two-hr-forecast`
- **UV Index**: `https://api-open.data.gov.sg/v2/real-time/api/uv-index`
- **Heat Index**: Combine `air-temperature` and `relative-humidity` from the nearest station.

### Messaging Logic
The briefing will be sent at **11:15 AM SGT**.
- **Proactive Ping**: The bot will notify the group if:
  - It is raining (existing).
  - UV Index is **High** (> 6).
  - "Feels Like" temperature is **Extreme** (> 33°C).
- **Format**:
  > 🍱 **Lunch Briefing for 8 Kallang Sector**
  > ⛅ **Forecast**: Partly Cloudy.
  > 🧴 **UV Index**: 7 (High). 
  > 🌡️ **Feels Like**: 34°C.

## 2. Feature: Custom Titles (Social Leaderboard)
Add engagement by awarding titles based on the user's total votes in Redis.

### Titles Mapping
- **3+ Votes**: 🎖️ **Kallang Loyal**
- **5+ Votes**: 👑 **Lunch King**

### UI Changes
Update the `/leaderboard` command to append the title next to the username.
> 🥇 @user1: 7 days **(Lunch King 👑)**

## 3. Technical Implementation
- **Files Affected**:
  - `lunch_bot.py`: Main logic for fetching UV/Heat and calculating titles.
  - `index.py`: Updating the `/weather` command to show full briefing.
- **Persistence**: Using existing Upstash Redis Rest client.
- **Dependencies**: No new dependencies (using existing `requests`).

---
*Created on: 2026-04-07*

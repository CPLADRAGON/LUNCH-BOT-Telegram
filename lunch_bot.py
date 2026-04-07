import os
import requests
import holidays
from datetime import datetime, timedelta
import pytz
import argparse
from upstash_redis import Redis

def get_sg_now():
    sg_tz = pytz.timezone('Asia/Singapore')
    return datetime.now(sg_tz)

def is_working_day(date_to_check=None):
    if date_to_check is None:
        now = get_sg_now()
        date_to_check = now.date()
    if date_to_check.weekday() >= 5: return False
    sg_holidays = holidays.country_holidays('SG')
    if date_to_check in sg_holidays: return False
    return True

def get_redis_client():
    url = os.getenv('UPSTASH_REDIS_REST_URL')
    token = os.getenv('UPSTASH_REDIS_REST_TOKEN')
    if not (url and token):
        print("Redis credentials missing.")
        return None
    return Redis(url=url, token=token)

def send_telegram_message(text, chat_id=None):
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = chat_id or os.getenv('TELEGRAM_CHAT_ID')
    if not (token and chat_id): return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

def send_lunch_poll():
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    if not (token and chat_id): return
    url = f"https://api.telegram.org/bot{token}/sendPoll"
    payload = {
        "chat_id": chat_id,
        "question": "🍱 Who's coming for lunch today?",
        "options": ["I'm in! 🙋‍♂️", "Not today 🙅‍♂️"],
        "is_anonymous": False,
        "allows_multiple_answers": False
    }
    requests.post(url, json=payload)

def check_weather(manual=False):
    TARGET_AREA = "Kallang"
    url = "https://api-open.data.gov.sg/v2/real-time/api/two-hr-forecast"
    print(f"Weather: Checking for {TARGET_AREA} (manual={manual})")
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            items = data.get('data', {}).get('items', []) or data.get('items', [])
            forecasts = items[0].get('forecasts', []) if items else []
            target = next((f for f in forecasts if f['area'] == TARGET_AREA), None)
            
            if target:
                forecast = target['forecast']
                cond = forecast.lower()
                is_rainy = any(w in cond for w in ["rain", "showers", "thunderstorm", "storm"])
                
                if is_rainy:
                    msg = f"☔ Heads up for 8 Kallang Sector! The forecast says '{forecast}'. Don't forget your umbrellas! ⛈️"
                    send_telegram_message(msg)
                elif manual:
                    msg = f"☀️ Forecast for 8 Kallang Sector: '{forecast}'. Looks good for lunch! 🍱"
                    send_telegram_message(msg)
            elif manual:
                send_telegram_message("⚠️ Could not find forecast for Kallang. Check again later!")
    except Exception as e:
        print(f"Weather error: {e}")

def update_redis_score(username):
    redis = get_redis_client()
    if not redis: return
    # Key: lunch_leaderboard
    redis.hincrby("lunch_leaderboard", username.lower(), 1)
    print(f"Redis: Incremented score for {username}")

def get_leaderboard_text(is_monthly=False):
    redis = get_redis_client()
    if not redis: return "Redis connection failed."
    
    data = redis.hgetall("lunch_leaderboard")
    if not data: return "No votes recorded yet! 🍱"

    # Convert bytes to strings and sort
    processed_data = {k: int(v) for k, v in data.items()}
    sorted_lb = sorted(processed_data.items(), key=lambda x: x[1], reverse=True)
    
    title = "🏆 Monthly Lunch Leaderboard" if is_monthly else "📊 Current Lunch Leaderboard"
    lines = [f"{title}:"]
    for i, (name, count) in enumerate(sorted_lb[:10], 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "🔹"
        lines.append(f"{medal} @{name}: {count} days")
    
    if is_monthly:
        redis.delete("lunch_leaderboard") # Reset
        lines.append("\n🎉 Monthly stats have been reset!")
    
    return "\n".join(lines)

def remind_non_voters():
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    regulars_raw = os.getenv('REGULARS', "")
    if not (token and chat_id) or not regulars_raw: return
    
    regulars = [r.strip().lstrip('@') for r in regulars_raw.split(',') if r.strip()]
    
    # We can't easily check "who voted today" in Redis without a second key
    # But since we have the webhook now, we could theoretically keep a "voted_today" set.
    # For now, let's just use the getUpdates fallback.
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    response = requests.get(url, params={"allowed_updates": ["poll_answer"]})
    if response.status_code == 200:
        voted = {up['poll_answer']['user']['username'].lower() for up in response.json().get('result', []) if 'poll_answer' in up and up['poll_answer'].get('user', {}).get('username')}
        missing = [r for r in regulars if r.lower() not in voted]
        if missing:
            mentions = " ".join([f"@{m}" for m in missing])
            send_telegram_message(f"📢 Gentle reminder for {mentions}: Don't forget to vote for lunch! 🍱")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['poll', 'remind', 'weather', 'tally', 'monthly', 'manual', 'auto'], default='auto')
    args = parser.parse_args()

    if not is_working_day(): exit(0)

    mode = args.mode
    if mode == 'auto':
        now = get_sg_now()
        if now.hour == 11 and now.minute < 10: mode = 'poll'
        elif now.hour == 11 and now.minute < 18: mode = 'weather'
        elif now.hour == 11: mode = 'remind'
        else: mode = 'manual'

    if mode == 'poll':
        send_lunch_poll()
    elif mode == 'weather':
        check_weather()
    elif mode == 'remind':
        remind_non_voters()
    elif mode == 'manual':
        send_telegram_message(get_leaderboard_text())
    elif mode == 'monthly':
        send_telegram_message(get_leaderboard_text(is_monthly=True))

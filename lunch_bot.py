import os
import requests
import holidays
from datetime import datetime, timedelta
import pytz
import argparse
from upstash_redis import Redis
from concurrent.futures import ThreadPoolExecutor
import json
from google import genai

# Persistent session for connection pooling
session = requests.Session()

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
    env_chat_id = os.getenv('TELEGRAM_CHAT_ID')
    chat_id = chat_id or env_chat_id
    
    if not token or not chat_id:
        print(f"ERROR: Telegram components missing. Token present: {bool(token)}, Chat ID present: {bool(chat_id)}")
        print(f"Available env keys: {list(os.environ.keys())}")
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id, 
        "text": text,
        "parse_mode": "HTML"
    }
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        print(f"Telegram API Error: {response.status_code} - {response.text}")
    else:
        print("Telegram message sent successfully.")

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

from concurrent.futures import ThreadPoolExecutor

# Persistent session for connection pooling
session = requests.Session()

def get_heat_index(temp, rh):
    """Simple Heat Index formula (approximation)."""
    return temp + (0.1 * (rh - 50)) if rh > 50 else temp

def fetch_json(url):
    try:
        return session.get(url, timeout=5).json()
    except Exception as e:
        print(f"Fetch error for {url}: {e}")
        return {}

def check_weather(manual=False, chat_id=None):
    TARGET_AREA = "Kallang"
    # V1 Public APIs (No-Auth)
    urls = {
        "forecast": "https://api.data.gov.sg/v1/environment/2-hour-weather-forecast",
        "uv": "https://api.data.gov.sg/v1/environment/uv-index",
        "temp": "https://api.data.gov.sg/v1/environment/air-temperature",
        "rh": "https://api.data.gov.sg/v1/environment/relative-humidity"
    }

    msg_lines = [f"🍱 <b>Lunch Briefing for {TARGET_AREA}</b>"]
    results = {}

    # 🚀 Fetch all APIs simultaneously (Save ~1.5s)
    with ThreadPoolExecutor(max_workers=4) as executor:
        future_to_url = {executor.submit(fetch_json, url): key for key, url in urls.items()}
        for future in future_to_url:
            key = future_to_url[future]
            results[key] = future.result()

    rain_alert = False
    uv_val = 0
    real_feel = 0
    forecast = "Unknown"

    try:
        # 1. Parse Forecast
        items = results.get("forecast", {}).get('items', [])
        if items:
            f_list = items[0].get('forecasts', [])
            target = next((f for f in f_list if f['area'] == TARGET_AREA), None)
            if target:
                forecast = target['forecast']
                if any(w in forecast.lower() for w in ["rain", "showers", "thunderstorm", "storm"]):
                    rain_alert = True
        msg_lines.append(f"⛅ <b>Forecast</b>: {forecast}")

        # 2. Parse UV
        uv_items = results.get("uv", {}).get('items', [])
        if uv_items:
            uv_data = uv_items[0].get('index', [])
            if uv_data:
                uv_val = uv_data[0].get('value', 0)
                uv_desc = "Low" if uv_val <= 2 else "Mod" if uv_val <= 5 else "High" if uv_val <= 7 else "Very High" if uv_val <= 10 else "Extreme"
                msg_lines.append(f"🧴 <b>UV Index</b>: {uv_val} ({uv_desc})")

        # 3. Parse Temp & RH
        t_items = results.get("temp", {}).get('items', [])
        rh_items = results.get("rh", {}).get('items', [])
        
        if t_items and rh_items:
            # Use the first station reading as proxy
            temp = t_items[0].get('readings', [{}])[0].get('value', 30)
            rh = rh_items[0].get('readings', [{}])[0].get('value', 70)
            real_feel = round(get_heat_index(temp, rh), 1)
            msg_lines.append(f"🌡️ <b>Feels Like</b>: {real_feel}°C")

        # Decision: Send message?
        msg = "\n".join(msg_lines)
        if manual:
            send_telegram_message(msg, chat_id=chat_id)
        elif rain_alert or uv_val >= 6 or real_feel >= 33:
            send_telegram_message(msg, chat_id=chat_id)
            
    except Exception as e:
        print(f"Briefing error: {e}")

def update_redis_score(username):
    redis = get_redis_client()
    if not redis: return
    # Key: lunch_leaderboard
    redis.hincrby("lunch_leaderboard", username.lower(), 1)
    print(f"Redis: Incremented score for {username}")

def get_voted_key():
    now = get_sg_now()
    return f"voted_today:{now.strftime('%Y-%m-%d')}"

def record_vote(username):
    redis = get_redis_client()
    if not redis: return
    key = get_voted_key()
    redis.sadd(key, username.lower())
    redis.expire(key, 86400) # Self-clean in 24 hours
    print(f"Redis: Recorded daily vote for {username}")

def get_leaderboard_text(is_monthly=False):
    redis = get_redis_client()
    if not redis: return "Redis connection failed."
    
    data = redis.hgetall("lunch_leaderboard")
    if not data: return "No votes recorded yet! 🍱"

    # Convert bytes to strings and sort
    processed_data = {k: int(v) for k, v in data.items()}
    sorted_lb = sorted(processed_data.items(), key=lambda x: x[1], reverse=True)
    
    title = "🏆 <b>Monthly Lunch Leaderboard</b>" if is_monthly else "📊 <b>Current Lunch Leaderboard</b>"
    lines = [f"{title}:"]
    
    for i, (name, count) in enumerate(sorted_lb[:10], 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "🔹"
        
        # Calculate Title
        user_title = ""
        if count >= 5: user_title = " (Lunch King 👑)"
        elif count >= 3: user_title = " (Kallang Loyal 🎖️)"
        
        lines.append(f"{medal} @{name}: {count} days{user_title}")
    
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
    
    # 🕵️ Check Redis for who voted today (Webhooks made getUpdates obsolete)
    redis = get_redis_client()
    if not redis: return
    voted_list = redis.smembers(get_voted_key())
    voted = {v.lower() for v in (voted_list or [])}
    
    missing = [r for r in regulars if r.lower() not in voted]
    
    if missing:
        mentions = " ".join([f"@{m}" for m in missing])
        msg = f"📢 <b>Gentle reminder for {mentions}:</b>\nDon't forget to vote for lunch! 🍱"
        send_telegram_message(msg)
    else:
        print("Everyone has voted!")

def is_last_working_day_of_month(date_to_check=None):
    if date_to_check is None:
        now = get_sg_now()
        date_to_check = now.date()
    
    if not is_working_day(date_to_check):
        return False
    
    # Check if there are any working days left in the same month
    curr_day = date_to_check
    next_day = curr_day + timedelta(days=1)
    
    while next_day.month == curr_day.month:
        if is_working_day(next_day):
            return False
        next_day += timedelta(days=1)
    
    return True

def get_ai_hype(prompt_type="scheduled", user_query=None):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "GEMINI_API_KEY is missing! I'm hype-less! 😱"
    
    try:
        client = genai.Client(api_key=api_key)
        # Using gemini-3.1-flash-lite-preview (Current public preview)
        model_id = 'gemini-3.1-flash-lite-preview' 
        
        system_instruction = (
            "You are the Energetic Hype-Bot for a Singapore team in Kallang. "
            "Your goal is to build massive hype for lunch. Be extremely energetic and "
            "enthusiastic, use lots of emojis (🍱,🚀,🔥), keep the tone friendly and "
            "conversational (avoid using all-caps), and mention local "
            "Singapore food culture where possible (Makan, Laksa, Chicken Rice, Hawker centers). "
            "Stay professional but fun. Keep responses under 50 words."
        )
        
        if prompt_type == "scheduled":
            full_prompt = f"{system_instruction} Generate a short morning hype message for the team (it is currently 10:45 AM)."
        elif prompt_type == "manual":
            full_prompt = f"{system_instruction} Someone asked for hype! Give them a burst of energy in 20 words or less!"
        elif prompt_type == "tally":
            top_names = user_query or "our champions"
            full_prompt = f"{system_instruction} We are broadcasting the lunch leaderboard. Our top performers are: {top_names}. Give them a celebratory call-out and encourage the rest to catch up!"
        else:
            full_prompt = f"{system_instruction} The user asked you this: '{user_query}'. Reply in your hype persona!"

        response = client.models.generate_content(
            model=model_id,
            contents=full_prompt
        )
        return response.text
    except Exception as e:
        print(f"Gemini Error: {e}")
        return "I'm having a brain freeze! 🧠❄️ But lunch is still going to be EPIC! 🔥🍱"

def send_ai_hype(chat_id=None, prompt_type="scheduled", query=None):
    chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")
    message = get_ai_hype(prompt_type=prompt_type, user_query=query)
    send_telegram_message(message, chat_id=chat_id)

def send_leaderboard_tally():
    redis = get_redis_client()
    if not redis: return
    
    data = redis.hgetall("lunch_leaderboard")
    if not data:
        send_telegram_message("📊 The leaderboard is currently empty. Let's start voting! 🍱")
        return

    processed_data = {k: int(v) for k, v in data.items()}
    sorted_lb = sorted(processed_data.items(), key=lambda x: x[1], reverse=True)
    
    # Get top 3 (or fewer) for AI cheer
    top_performers = [f"@{name}" for name, _ in sorted_lb[:3]]
    cheer_names = ", ".join(top_performers)
    
    # 1. Get AI Cheer
    ai_cheer = get_ai_hype(prompt_type="tally", user_query=cheer_names)
    
    # 2. Get standard leaderboard text
    lb_text = get_leaderboard_text()
    
    # 3. Combine and send
    full_msg = f"🍱 <b>LUNCH STANDINGS TALLY</b> 📊\n\n{ai_cheer}\n\n{lb_text}"
    send_telegram_message(full_msg)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['poll', 'remind', 'weather', 'tally', 'monthly', 'manual', 'auto', 'hype'], default='auto')
    args = parser.parse_args()

    if not is_working_day(): exit(0)

    mode = args.mode
    if mode == 'auto':
        now = get_sg_now()
        # Fallback logic if no mode passed, but we prefer explicit modes now
        if now.hour == 11 and now.minute < 15: mode = 'poll'
        elif now.hour == 11 and now.minute < 20: mode = 'weather'
        elif now.hour == 11: mode = 'remind'
        else: mode = 'manual'

    if mode == 'poll':
        send_lunch_poll()
    elif mode == 'weather':
        check_weather()
    elif mode == 'remind':
        remind_non_voters()
    elif mode == 'tally':
        send_leaderboard_tally()
    elif mode == 'manual':
        send_telegram_message(get_leaderboard_text())
    elif mode == 'monthly':
        if is_last_working_day_of_month():
            send_telegram_message(get_leaderboard_text(is_monthly=True))
        else:
            print("Monthly trigger fired, but it's not the last working day of the month. Skipping reset.")
    elif mode == 'hype':
        send_ai_hype(prompt_type='scheduled')

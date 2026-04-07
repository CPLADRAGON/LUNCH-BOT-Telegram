import os
import requests
import holidays
from datetime import datetime
import pytz

def is_working_day():
    # Singapore timezone
    sg_tz = pytz.timezone('Asia/Singapore')
    now = datetime.now(sg_tz)
    
    # Check if weekend (Saturday=5, Sunday=6)
    if now.weekday() >= 5:
        print(f"Skipping: {now.date()} is a weekend.")
        return False
        
    # Check if Singapore Public Holiday
    sg_holidays = holidays.country_holidays('SG')
    if now.date() in sg_holidays:
        print(f"Skipping: {now.date()} is a holiday ({sg_holidays.get(now.date())}).")
        return False
        
    return True

def send_lunch_poll():
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not token or not chat_id:
        print("Error: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set.")
        return

    url = f"https://api.telegram.org/bot{token}/sendPoll"
    
    payload = {
        "chat_id": chat_id,
        "question": "🍱 Who's coming for lunch today?",
        "options": ["I'm in! 🙋‍♂️", "Not today 🙅‍♂️"],
        "is_anonymous": False,
        "allows_multiple_answers": False
    }
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        print("Success: Lunch poll sent!")
    else:
        print(f"Error: Failed to send poll. Status: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    if is_working_day():
        send_lunch_poll()
    else:
        print("Today is not a working day. No poll sent.")

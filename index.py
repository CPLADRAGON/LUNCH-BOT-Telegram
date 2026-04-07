from flask import Flask, request
import sys
import os
import lunch_bot

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        return "🚀 Singapore Lunch Bot is Live!", 200

    update = request.get_json()
    if not update:
        return "No JSON provided", 400
    
    # 1. Handle Commands
    if "message" in update and "text" in update["message"]:
        text = update["message"]["text"].lower()
        chat_id = update["message"]["chat"]["id"]
        
        if "/weather" in text:
            os.environ['TELEGRAM_CHAT_ID'] = str(chat_id)
            lunch_bot.check_weather(manual=True)
        
        elif "/leaderboard" in text:
            os.environ['TELEGRAM_CHAT_ID'] = str(chat_id)
            lb_text = lunch_bot.get_leaderboard_text()
            lunch_bot.send_telegram_message(lb_text, chat_id=chat_id)

    # 2. Handle Poll Answers (Instant Tally)
    if "poll_answer" in update:
        answer = update["poll_answer"]
        if answer.get("option_ids") == [0]:
            user = answer.get("user", {})
            username = user.get("username")
            if username:
                lunch_bot.update_redis_score(username)
                lunch_bot.record_vote(username)

    return "OK", 200

if __name__ == "__main__":
    app.run(port=5000)

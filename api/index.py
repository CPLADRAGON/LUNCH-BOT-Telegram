from flask import Flask, request, jsonify
import sys
import os

# Ensure the root directory is in sys.path so we can import lunch_bot
sys.path.append(os.getcwd())
import lunch_bot

app = Flask(__name__)

@app.route("/", methods=["POST"])
def webhook():
    update = request.get_json()
    
    # 1. Handle Commands
    if "message" in update and "text" in update["message"]:
        text = update["message"]["text"].lower()
        chat_id = update["message"]["chat"]["id"]
        
        if "/weather" in text:
            # We want to send the reply to the chat where the command came from
            os.environ['TELEGRAM_CHAT_ID'] = str(chat_id)
            lunch_bot.check_weather()
        
        elif "/leaderboard" in text:
            os.environ['TELEGRAM_CHAT_ID'] = str(chat_id)
            lb_text = lunch_bot.get_leaderboard_text()
            lunch_bot.send_telegram_message(lb_text, chat_id=chat_id)

    # 2. Handle Poll Answers (Instant Tally)
    if "poll_answer" in update:
        answer = update["poll_answer"]
        # Only tally if they picked the first option ("I'm in!")
        if answer.get("option_ids") == [0]:
            user = answer.get("user", {})
            username = user.get("username")
            if username:
                lunch_bot.update_redis_score(username)

    return "OK", 200

# For local testing
if __name__ == "__main__":
    app.run(port=5000)

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
            lunch_bot.check_weather(manual=True, chat_id=chat_id)
        
        elif "/leaderboard" in text:
            lb_text = lunch_bot.get_leaderboard_text()
            lunch_bot.send_telegram_message(lb_text, chat_id=chat_id)

        elif "/hype" in text:
            lunch_bot.send_ai_hype(chat_id=chat_id, prompt_type="manual")

        else:
            # Handle Mentions and DMs
            is_private = update["message"]["chat"]["type"] == "private"
            bot_username = os.getenv("BOT_USERNAME", "@LunchBot").lower()
            
            if is_private or bot_username in text:
                # Remove mention from query for cleaner AI response
                query = text.replace(bot_username, "").strip()
                lunch_bot.send_ai_hype(chat_id=chat_id, prompt_type="chat", query=query)

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

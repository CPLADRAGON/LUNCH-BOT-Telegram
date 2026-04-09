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

@app.route("/api/cron", methods=["POST"])
def cron_trigger():
    print(f"--- CRON TRIGGER START [Mode: {request.args.get('mode')}] ---")
    
    # 1. Verification
    auth_header = request.headers.get("Authorization")
    query_secret = request.args.get("secret")
    cron_secret = os.getenv("CRON_SECRET")
    
    print(f"Auth Check: Header={bool(auth_header)}, Query={bool(query_secret)}")
    
    if not cron_secret:
        print("Error: CRON_SECRET not set in Environment Variables")
        return "CRON_SECRET not configured on server", 500
        
    authorized = (auth_header == f"Bearer {cron_secret}") or (query_secret == cron_secret)
    if not authorized:
        print("Error: Unauthorized trigger attempt")
        return "Unauthorized", 401

    # 2. Daily Working Day Check
    is_wd = lunch_bot.is_working_day()
    print(f"Working Day Check: {is_wd}")
    if not is_wd:
        return "Skipping: Not a working day in Singapore", 200

    # 3. Mode Dispatcher
    mode = request.args.get("mode", "auto")
    print(f"Executing Mode: {mode}")
    
    try:
        if mode == 'hype':
            lunch_bot.send_ai_hype(prompt_type='scheduled')
        elif mode == 'poll':
            lunch_bot.send_lunch_poll()
        elif mode == 'weather':
            lunch_bot.check_weather()
        elif mode == 'remind':
            lunch_bot.remind_non_voters()
        elif mode == 'tally':
            print("Dispatching tally task...")
            lunch_bot.send_leaderboard_tally()
        elif mode == 'monthly':
            if lunch_bot.is_last_working_day_of_month():
                lunch_bot.send_telegram_message(lunch_bot.get_leaderboard_text(is_monthly=True))
        else:
            print(f"Error: Invalid mode '{mode}'")
            return f"Invalid or missing mode: {mode}", 400
            
        print(f"SUCCESS: Job {mode} completed")
        return f"Job executed successfully: {mode}", 200
    except Exception as e:
        print(f"CRITICAL ERROR in cron job: {e}")
        import traceback
        traceback.print_exc()
        return f"Error executing job: {str(e)}", 500

# For local testing
if __name__ == "__main__":
    app.run(port=5000)

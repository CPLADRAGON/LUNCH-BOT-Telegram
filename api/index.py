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
    
    # 1. Handle Messages (Commands, joins, leaves)
    if "message" in update:
        message = update["message"]
        chat_id = message["chat"]["id"]
        
        # A. Handle Automated Chat Event Listeners (Join/Leave)
        if "new_chat_members" in message:
            for member in message["new_chat_members"]:
                # Filter out bots
                if member.get("is_bot"):
                    continue
                username = member.get("username")
                if username:
                    lunch_bot.add_regular(username)
                    # Celebrate with Gemini Hype!
                    hype_msg = lunch_bot.get_ai_hype(prompt_type="onboard", user_query=f"@{username}")
                    lunch_bot.send_telegram_message(hype_msg, chat_id=chat_id)
                    
        elif "left_chat_member" in message:
            member = message["left_chat_member"]
            if not member.get("is_bot"):
                username = member.get("username")
                if username:
                    lunch_bot.remove_regular(username)
                    # Say goodbye with Gemini Hype!
                    hype_msg = lunch_bot.get_ai_hype(prompt_type="offboard", user_query=f"@{username}")
                    lunch_bot.send_telegram_message(hype_msg, chat_id=chat_id)
        
        # B. Handle Text-based Commands
        elif "text" in message:
            text = message["text"].lower()
            print(f"--- TELEGRAM_MESSAGE Received ---")
            print(f"Chat ID: {chat_id}")
            print(f"---------------------------------")
            
            # Existing commands
            if "/weather" in text:
                lunch_bot.check_weather(manual=True, chat_id=chat_id)
            
            elif "/leaderboard" in text:
                lb_text = lunch_bot.get_leaderboard_text()
                lunch_bot.send_telegram_message(lb_text, chat_id=chat_id)
    
            elif "/missing" in text:
                missing_text = lunch_bot.get_non_voters_text()
                lunch_bot.send_telegram_message(missing_text, chat_id=chat_id)
    
            elif "/hype" in text:
                lunch_bot.send_ai_hype(chat_id=chat_id, prompt_type="manual")
                
            # Dynamic Onboarding / Offboarding commands
            elif "/onboard" in text or "/join" in text:
                # Determine target user
                target_user = None
                words = message["text"].split()
                if len(words) > 1:
                    arg = words[1].strip()
                    if arg:
                        target_user = arg.lstrip("@")
                
                # Default to sender if no argument provided
                if not target_user:
                    user = message.get("from", {})
                    target_user = user.get("username")
                
                if target_user:
                    lunch_bot.add_regular(target_user)
                    hype_msg = lunch_bot.get_ai_hype(prompt_type="onboard", user_query=f"@{target_user}")
                    lunch_bot.send_telegram_message(hype_msg, chat_id=chat_id)
                else:
                    lunch_bot.send_telegram_message("❌ Error: Could not detect username. Please make sure you have a Telegram username set!", chat_id=chat_id)
            
            elif "/offboard" in text or "/leave" in text:
                # Determine target user
                target_user = None
                words = message["text"].split()
                if len(words) > 1:
                    arg = words[1].strip()
                    if arg:
                        target_user = arg.lstrip("@")
                        
                # Default to sender if no argument provided
                if not target_user:
                    user = message.get("from", {})
                    target_user = user.get("username")
                    
                if target_user:
                    lunch_bot.remove_regular(target_user)
                    hype_msg = lunch_bot.get_ai_hype(prompt_type="offboard", user_query=f"@{target_user}")
                    lunch_bot.send_telegram_message(hype_msg, chat_id=chat_id)
                else:
                    lunch_bot.send_telegram_message("❌ Error: Could not detect username. Please make sure you have a Telegram username set!", chat_id=chat_id)
    
            else:
                # Handle Mentions and DMs
                is_private = message["chat"]["type"] == "private"
                bot_username = os.getenv("BOT_USERNAME", "@LunchBot").lower()
                
                if is_private or bot_username in text:
                    # Remove mention from query for cleaner AI response
                    query = text.replace(bot_username, "").strip()
                    lunch_bot.send_ai_hype(chat_id=chat_id, prompt_type="chat", query=query)

    # 2. Handle Poll Answers (Instant Tally)
    if "poll_answer" in update:
        answer = update["poll_answer"]
        user = answer.get("user", {})
        username = user.get("username")
        
        if username:
            option_ids = answer.get("option_ids", [])
            if option_ids:
                # 1. Record that they voted today (to remove from "missing" list)
                lunch_bot.record_vote(username)
                
                # 2. Only tally score if they picked the first option ("I'm in!")
                if option_ids == [0]:
                    lunch_bot.update_redis_score(username)

    return "OK", 200

@app.route("/api/cron", methods=["POST"])
def cron_trigger():
    mode = request.args.get("mode", "auto")
    print(f"--- CRON TRIGGER START [Mode: {mode}] ---")
    
    try:
        # 1. Verification
        auth_header = request.headers.get("Authorization")
        query_secret = request.args.get("secret")
        cron_secret = os.getenv("CRON_SECRET")
        
        if not cron_secret:
            return "Internal Error: CRON_SECRET missing", 500
            
        authorized = (auth_header == f"Bearer {cron_secret}") or (query_secret == cron_secret)
        if not authorized:
            print("Error: Unauthorized trigger attempt")
            return "Unauthorized", 401

        # 2. Daily Working Day Check
        if not lunch_bot.is_working_day():
            print("Skipping: Not a working day in Singapore.")
            return "Skipped: Weekend/Holiday", 200

        # 3. Mode Dispatcher
        if mode == 'hype':
            lunch_bot.send_ai_hype(prompt_type='scheduled')
        elif mode == 'poll':
            lunch_bot.send_lunch_poll()
        elif mode == 'weather':
            lunch_bot.check_weather()
        elif mode == 'remind':
            lunch_bot.remind_non_voters()
        elif mode == 'tally':
            lunch_bot.send_leaderboard_tally()
        elif mode == 'monthly':
            if lunch_bot.is_last_working_day_of_month():
                lunch_bot.send_telegram_message(lunch_bot.get_leaderboard_text(is_monthly=True))
        else:
            return f"Invalid mode: {mode}", 400
            
        return f"Success: {mode}", 200

    except Exception as e:
        print(f"CRITICAL ERROR in {mode}: {e}")
        return f"Error: {str(e)}", 500

# For local testing
if __name__ == "__main__":
    app.run(port=5000)

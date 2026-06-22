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
            
            if "/weather" in text:
                os.environ['TELEGRAM_CHAT_ID'] = str(chat_id)
                lunch_bot.check_weather(manual=True, chat_id=chat_id)
            
            elif "/leaderboard" in text:
                os.environ['TELEGRAM_CHAT_ID'] = str(chat_id)
                lb_text = lunch_bot.get_leaderboard_text()
                lunch_bot.send_telegram_message(lb_text, chat_id=chat_id)
                
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

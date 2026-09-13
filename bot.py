import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import time
import os
import traceback
from backend import analyze_grievance, save_complaint, get_ticket_status, get_nearest_office

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

# Temporary memory to hold loose data per user
user_sessions = {}

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "🏛️ *Welcome to JanSeva AI Citizen Bot*\nSend a photo/video and share your location to file a grievance.", parse_mode="Markdown")

@bot.message_handler(func=lambda msg: msg.text and msg.text.upper().startswith("STATUS"))
def track_status(message):
    try:
        ticket_id = message.text.upper().split()[1].strip()
        result = get_ticket_status(ticket_id)
        if result:
            bot.reply_to(message, f"📌 *ID:* `{ticket_id}`\n📊 *Status:* {result[0]}\n🏢 *Department:* {result[1]}", parse_mode="Markdown")
        else:
            bot.reply_to(message, "❌ Ticket not found.")
    except:
        bot.reply_to(message, "⚠️ Error checking status.")

@bot.message_handler(content_types=['text', 'photo', 'video', 'voice', 'audio', 'document', 'animation'])
def process_media(message):
    chat_id = str(message.chat.id)
    complaint_text = ""
    file_id = ""

    if chat_id not in user_sessions:
        user_sessions[chat_id] = {"text": "", "file_id": ""}

    try:
        if message.content_type == 'text':
            # Ignore status or command texts here
            if message.text.startswith('/'): return
            complaint_text = message.text
            user_sessions[chat_id]["text"] = complaint_text
        elif message.content_type == 'photo':
            complaint_text = message.caption or "Visual public hazard."
            file_id = message.photo[-1].file_id
            user_sessions[chat_id]["text"] = complaint_text
            user_sessions[chat_id]["file_id"] = file_id
        elif message.content_type == 'video':
            complaint_text = message.caption or "Video of public hazard."
            file_id = message.video.file_id
            user_sessions[chat_id]["text"] = complaint_text
            user_sessions[chat_id]["file_id"] = file_id
        elif message.content_type in ['voice', 'audio']:
            complaint_text = message.caption or "Audio grievance submission."
            file_id = message.voice.file_id if message.content_type == 'voice' else message.audio.file_id
            user_sessions[chat_id]["text"] = complaint_text
            user_sessions[chat_id]["file_id"] = file_id
        elif message.content_type in ['document', 'animation']:
            complaint_text = message.caption or "Attached media file."
            file_id = message.document.file_id if message.content_type == 'document' else message.animation.file_id
            user_sessions[chat_id]["text"] = complaint_text
            user_sessions[chat_id]["file_id"] = file_id

        # If we have text/media, prompt for location
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add(KeyboardButton("📍 Share Exact Location", request_location=True))
        
        bot.reply_to(message, "✅ Details captured!\n\nTap **📍 Share Exact Location** below to submit your grievance.", reply_markup=markup)
        
    except Exception as e:
        bot.reply_to(message, f"⚠️ Error: `{str(e)}`")

@bot.message_handler(content_types=['location'])
def process_location(message):
    chat_id = str(message.chat.id)
    lat = message.location.latitude
    lng = message.location.longitude
    
    # Fallback if they didn't send text/media first
    if chat_id not in user_sessions or not user_sessions[chat_id]["text"]:
        user_sessions[chat_id] = {"text": "General location grievance report.", "file_id": ""}

    bot.reply_to(message, "⏳ *Analyzing and routing to nearest ward...*", parse_mode="Markdown", reply_markup=ReplyKeyboardRemove())
    
    try:
        data = user_sessions[chat_id]
        ward = get_nearest_office(lat, lng)
        ai_decision = analyze_grievance(data["text"])
        
        ticket_id = save_complaint(ward, data["text"], ai_decision, chat_id, data["file_id"], lat, lng)
        
        reply = (f"✅ *Grievance Dispatched!*\n\n🎫 *ID:* `{ticket_id}`\n📍 *Routed To:* {ward}\n🏢 *Dept:* {ai_decision.get('department', 'Civic Body')}\n⚡ *Severity:* {ai_decision.get('severity', 'Medium')}")
        bot.reply_to(message, reply, parse_mode="Markdown")
        
        # Clear session
        user_sessions[chat_id] = {"text": "", "file_id": ""}
        
    except Exception as e:
        bot.reply_to(message, f"⚠️ Database Routing Error: `{str(e)}`")

if __name__ == "__main__":
    print("🤖 Resilient Bot active...")
    bot.remove_webhook()
    time.sleep(1)
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
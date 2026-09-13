import os
import telebot
from telebot import types
from backend import save_grievance

bot = telebot.TeleBot(os.getenv("TELEGRAM_BOT_TOKEN"))
user_sessions = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "🏛️ JanSeva AI. Describe your issue or upload a photo/video/voice note:")

@bot.message_handler(content_types=['text', 'photo', 'video', 'voice', 'audio', 'document'])
def handle_media(message):
    cid = message.chat.id
    session = {"raw_text": message.text or message.caption or "Media Attached", "media_type": None, "media_file_id": None}
    
    if message.photo:
        session["media_type"], session["media_file_id"] = "photo", message.photo[-1].file_id
    elif message.video:
        session["media_type"], session["media_file_id"] = "video", message.video.file_id
    elif message.voice:
        session["media_type"], session["media_file_id"] = "voice", message.voice.file_id
    elif message.document:
        session["media_type"], session["media_file_id"] = "document", message.document.file_id
        
    user_sessions[cid] = session
    
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add(types.KeyboardButton("📍 Share Exact Location", request_location=True))
    bot.send_message(cid, "Evidence received. Now tap below to share your exact GPS location for the density scan:", reply_markup=markup)

@bot.message_handler(content_types=['location'])
def handle_location(message):
    cid = message.chat.id
    if cid not in user_sessions:
        bot.send_message(cid, "Please describe your issue or upload media first.")
        return

    lat, lon = message.location.latitude, message.location.longitude
    s = user_sessions[cid]
    u_name = message.from_user.first_name
    
    bot.reply_to(message, "⏳ AI Triage & 50m Density Scan in progress...", reply_markup=types.ReplyKeyboardRemove())
    
    res = save_grievance(cid, u_name, s["raw_text"], s["media_type"], s["media_file_id"], lat, lon)
    
    msg = (f"✅ **Grievance Registered!**\n\n🎫 ID: `{res['ticket_id']}`\n"
           f"📁 Category: {res['category']}\n⚡ Priority: {res['severity']}\n"
           f"📝 AI Summary: {res['summary']}")
    bot.send_message(cid, msg, parse_mode="Markdown")
    del user_sessions[cid]

if __name__ == "__main__":
    bot.infinity_polling()
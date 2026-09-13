import os
import telebot
from telebot import types
from backend import save_grievance

bot = telebot.TeleBot(os.getenv("TELEGRAM_BOT_TOKEN"))
user_sessions = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "🏛️ JanSeva AI. Please type your civic complaint (e.g., 'Broken pipe flooding the street').")

@bot.message_handler(content_types=['text'])
def handle_text(message):
    user_sessions[message.chat.id] = {"raw_text": message.text}
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    # This button forces exact device GPS extraction
    markup.add(types.KeyboardButton("📍 Share Exact Location", request_location=True))
    bot.send_message(message.chat.id, "Please share your exact GPS location so we can scan for incident density in your 50m radius:", reply_markup=markup)

@bot.message_handler(content_types=['location'])
def handle_location(message):
    cid = message.chat.id
    if cid not in user_sessions:
        bot.send_message(cid, "Please describe your issue first.")
        return

    lat, lon = message.location.latitude, message.location.longitude
    raw_text = user_sessions[cid]["raw_text"]
    u_name = message.from_user.first_name
    
    bot.reply_to(message, "⏳ AI Triage & 50m Density Scan in progress...", reply_markup=types.ReplyKeyboardRemove())
    
    res = save_grievance(cid, u_name, raw_text, lat, lon)
    
    msg = (f"✅ **Grievance Registered!**\n\n🎫 ID: `{res['ticket_id']}`\n"
           f"📁 Category: {res['category']}\n⚡ Priority: {res['severity']}\n"
           f"📝 AI Summary: {res['summary']}")
    bot.send_message(cid, msg, parse_mode="Markdown")
    del user_sessions[cid]

if __name__ == "__main__":
    bot.infinity_polling()
import telebot
import time
import os
from backend import analyze_grievance, save_complaint, get_ticket_status

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "🏛️ *Welcome to JanSeva AI Citizen Bot*\nLodge a text, photo, video, or voice complaint instantly.", parse_mode="Markdown")

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

@bot.message_handler(content_types=['text', 'photo', 'video', 'voice'])
def process_grievance(message):
    chat_id = str(message.chat.id)
    complaint_text = ""
    media_path = ""
    file_id = None
    ext = ""

    # Handle text or media captions
    if message.content_type == 'text':
        complaint_text = message.text
    elif message.content_type == 'photo':
        complaint_text = message.caption or "Visual public hazard."
        file_id = message.photo[-1].file_id
        ext = ".jpg"
    elif message.content_type == 'video':
        complaint_text = message.caption or "Video of public hazard."
        file_id = message.video.file_id
        ext = ".mp4"
    elif message.content_type == 'voice':
        complaint_text = "Audio grievance submission."
        file_id = message.voice.file_id
        ext = ".ogg"

    if not complaint_text.strip():
        bot.reply_to(message, "⚠️ Please include a caption.")
        return

    bot.reply_to(message, "⏳ *Analyzing and saving media...*", parse_mode="Markdown")

    # Download Media
    if file_id:
        os.makedirs("media", exist_ok=True)
        try:
            file_info = bot.get_file(file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            media_path = f"media/{file_id}{ext}"
            with open(media_path, 'wb') as new_file:
                new_file.write(downloaded_file)
        except Exception as e:
            print("Media download failed:", e)

    try:
        ai_decision = analyze_grievance(complaint_text)
        ticket_id = save_complaint("Ward 1 - Central", complaint_text, ai_decision, chat_id, media_path)

        reply = (f"✅ *Grievance Registered!*\n🎫 *ID:* `{ticket_id}`\n🏢 *Dept:* {ai_decision.get('department', 'Civic Body')}\n⚡ *Severity:* {ai_decision.get('severity', 'Medium')}")
        bot.reply_to(message, reply, parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, "⚠️ Failed to process.")

if __name__ == "__main__":
    print("🤖 Bot active...")
    bot.remove_webhook()
    time.sleep(1)
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
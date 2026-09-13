import telebot
import time
import os
import traceback
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

@bot.message_handler(content_types=['text', 'photo', 'video', 'voice', 'audio', 'document', 'animation'])
def process_grievance(message):
    chat_id = str(message.chat.id)
    complaint_text = ""
    file_id = ""

    try:
        if message.content_type == 'text':
            complaint_text = message.text
        elif message.content_type == 'photo':
            complaint_text = message.caption or "Visual public hazard."
            file_id = message.photo[-1].file_id
        elif message.content_type == 'video':
            complaint_text = message.caption or "Video of public hazard."
            file_id = message.video.file_id
        elif message.content_type == 'voice':
            complaint_text = message.caption or "Live audio grievance submission."
            file_id = message.voice.file_id
        elif message.content_type == 'audio':
            complaint_text = message.caption or "Uploaded audio grievance file."
            file_id = message.audio.file_id
        elif message.content_type in ['document', 'animation']:
            complaint_text = message.caption or "Attached media file."
            file_id = message.document.file_id if message.content_type == 'document' else message.animation.file_id

        if not complaint_text.strip():
            bot.reply_to(message, "⚠️ Please include a caption with your media.")
            return

        bot.reply_to(message, "⏳ *Analyzing grievance...*", parse_mode="Markdown")

        # Route through Gemini & Save the raw File ID
        ai_decision = analyze_grievance(complaint_text)
        ticket_id = save_complaint("Ward 1 - Central", complaint_text, ai_decision, chat_id, file_id)

        reply = (f"✅ *Grievance Registered!*\n🎫 *ID:* `{ticket_id}`\n🏢 *Dept:* {ai_decision.get('department', 'Civic Body')}\n⚡ *Severity:* {ai_decision.get('severity', 'Medium')}")
        bot.reply_to(message, reply, parse_mode="Markdown")
        
    except Exception as e:
        error_trace = traceback.format_exc()
        print(error_trace) 
        bot.reply_to(message, f"⚠️ System Error: `{str(e)}`")

if __name__ == "__main__":
    print("🤖 Universal Bot active...")
    bot.remove_webhook()
    time.sleep(1)
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
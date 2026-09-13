import telebot
import time
from backend import analyze_grievance, save_complaint, get_ticket_status

BOT_TOKEN = "8952553079:AAGoWGrfuMOhEy3QyGmV0_NcI8hI7mSBiZY"
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    text = (
        "🏛️ *Welcome to JanSeva AI Citizen Bot*\n\n"
        "You can lodge grievances directly from Telegram:\n"
        "• Send a **text message** describing the issue\n"
        "• Send a **photo / video** with a caption\n"
        "• Track an issue: `STATUS <Ticket-ID>`"
    )
    bot.reply_to(message, text, parse_mode="Markdown")

@bot.message_handler(func=lambda msg: msg.text and msg.text.upper().startswith("STATUS"))
def track_status(message):
    try:
        parts = message.text.upper().split()
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ Please provide a Ticket ID. Example: `STATUS GRV-0913111144`", parse_mode="Markdown")
            return

        ticket_id = parts[1].strip()
        result = get_ticket_status(ticket_id)

        if result:
            status, dept, summary = result
            reply = (
                f"🏛️ *JanSeva Grievance Update*\n\n"
                f"📌 *ID:* `{ticket_id}`\n"
                f"📊 *Status:* {status}\n"
                f"🏢 *Department:* {dept}\n"
                f"📝 *Summary:* {summary}"
            )
            bot.reply_to(message, reply, parse_mode="Markdown")
        else:
            bot.reply_to(message, "❌ Ticket not found in the live registry.")
    except Exception as e:
        bot.reply_to(message, "⚠️ Error checking ticket status.")

@bot.message_handler(content_types=['text', 'photo', 'video', 'voice'])
def process_grievance(message):
    # Extract complaint text from raw text or media caption
    complaint_text = ""
    if message.content_type == 'text':
        complaint_text = message.text
    elif message.content_type in ['photo', 'video']:
        complaint_text = message.caption or "Visual public hazard reported via citizen media upload."
    elif message.content_type == 'voice':
        complaint_text = "Audio grievance submission: Citizen reported emergency civic malfunction."

    if not complaint_text.strip():
        bot.reply_to(message, "⚠️ Please include a brief description or caption with your media.")
        return

    bot.reply_to(message, "⏳ *JanSeva AI is analyzing your report and assigning SLA priorities...*", parse_mode="Markdown")

    try:
        ward = "Ward 1 - Central"
        ai_decision = analyze_grievance(complaint_text)
        ticket_id = save_complaint(ward, complaint_text, ai_decision)

        reply = (
            f"✅ *Grievance Registered Successfully!*\n\n"
            f"🎫 *Ticket ID:* `{ticket_id}`\n"
            f"🏷️ *Category:* {ai_decision.get('category', 'General')}\n"
            f"🏢 *Department:* {ai_decision.get('department', 'Civic Body')}\n"
            f"⚡ *Severity:* {ai_decision.get('severity', 'Medium')}\n"
            f"📝 *Summary:* {ai_decision.get('summary', complaint_text[:60])}\n\n"
            f"Your issue has been dispatched to the Ward Officer Dashboard."
        )
        bot.reply_to(message, reply, parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, f"⚠️ Failed to process grievance: {str(e)}")

if __name__ == "__main__":
    print("🤖 JanSeva Bot polling active...")
    bot.remove_webhook()
    time.sleep(1)
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
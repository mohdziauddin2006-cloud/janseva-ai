import telebot
import sqlite3
import time

BOT_TOKEN = "8952553079:AAGoWGrfuMOhEy3QyGmV0_NcI8hI7mSBiZY"
bot = telebot.TeleBot(BOT_TOKEN)

def fetch_status_from_db(ticket_id):
    try:
        # The crucial fix for Streamlit Cloud threading: check_same_thread=False
        conn = sqlite3.connect("grievances.db", check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("SELECT status, department, summary FROM grievances WHERE id=?", (ticket_id,))
        result = cursor.fetchone()
        conn.close()
        return result
    except Exception as e:
        print(f"Database error: {e}")
        return None

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome to JanSeva AI. To check your grievance, reply with: STATUS <Your-Ticket-ID>")

@bot.message_handler(func=lambda message: message.text.upper().startswith("STATUS"))
def check_ticket_status(message):
    try:
        parts = message.text.upper().split()
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ Please provide your Ticket ID. Example: STATUS GRV-0913111144")
            return
            
        ticket_id = parts[1].strip()
        result = fetch_status_from_db(ticket_id)
        
        if result:
            status, dept, summary = result
            reply = f"🏛️ *JanSeva AI Ticket Update*\n\n*ID:* {ticket_id}\n*Status:* {status}\n*Department:* {dept}\n*Issue:* {summary}"
            bot.reply_to(message, reply, parse_mode="Markdown")
        else:
            bot.reply_to(message, "❌ Ticket not found in the live database. Please check the ID.")
            
    except Exception as e:
        bot.reply_to(message, "An error occurred while checking your status.")

def run_bot():
    try:
        bot.remove_webhook()
        time.sleep(2) # Give the website 2 seconds to boot up first
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        print(f"Bot crashed: {e}")
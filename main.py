import subprocess
import sys
import os

print("🚀 Starting JanSeva Master Protocol...")

# 1. Boot the Telegram Bot in the background
bot_process = subprocess.Popen([sys.executable, "bot.py"])
print("🤖 Bot process spawned.")

# 2. Boot the Streamlit Website in the foreground
port = os.environ.get("PORT", "8501")
streamlit_process = subprocess.Popen([
    sys.executable, "-m", "streamlit", "run", "app.py", 
    "--server.port", port, "--server.address", "0.0.0.0"
])
print("🌐 Streamlit process spawned.")

# Keep the container alive
bot_process.wait()
streamlit_process.wait()
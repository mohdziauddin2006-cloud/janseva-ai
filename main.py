import os
import sys
import subprocess
import signal
import time

def run_services():
    port = os.environ.get("PORT", "8501")
    print("🚀 Initializing JanSeva AI Multi-Service Protocol...")

    # 1. Start Telegram Bot background process
    bot_process = subprocess.Popen(
        [sys.executable, "bot.py"],
        stdout=sys.stdout,
        stderr=sys.stderr
    )
    print(f"🤖 Citizen Telegram Bot worker started (PID: {bot_process.pid})")

    # 2. Start Streamlit Officer Dashboard
    streamlit_cmd = [
        sys.executable, "-m", "streamlit", "run", "app.py",
        "--server.port", str(port),
        "--server.address", "0.0.0.0",
        "--server.headless", "true",
        "--browser.serverAddress", "0.0.0.0",
        "--server.enableCORS", "false",
        "--server.enableXsrfProtection", "false"
    ]
    
    streamlit_process = subprocess.Popen(
        streamlit_cmd,
        stdout=sys.stdout,
        stderr=sys.stderr
    )
    print(f"🌐 Ward Officer Web Portal bound to port {port} (PID: {streamlit_process.pid})")

    # 3. Clean shutdown handler for Render lifecycle signals
    def shutdown(signum, frame):
        print("\n🛑 Gracefully terminating all JanSeva child processes...")
        bot_process.terminate()
        streamlit_process.terminate()
        try:
            bot_process.wait(timeout=5)
            streamlit_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            bot_process.kill()
            streamlit_process.kill()
        sys.exit(0)

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    # 4. Process watchdog loop
    while True:
        # Auto-resurrect the bot if an unhandled network disconnect occurs
        if bot_process.poll() is not None:
            print("⚠️ Telegram bot process dropped. Resurrecting worker immediately...")
            bot_process = subprocess.Popen(
                [sys.executable, "bot.py"],
                stdout=sys.stdout,
                stderr=sys.stderr
            )

        # Exit main runner if the web server halts
        if streamlit_process.poll() is not None:
            print("🚨 Web dashboard service halted. Triggering shutdown...")
            shutdown(None, None)

        time.sleep(3)

if __name__ == "__main__":
    run_services()
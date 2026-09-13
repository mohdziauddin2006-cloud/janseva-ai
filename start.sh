#!/bin/bash
# Start the Telegram bot in the background
python bot.py &
# Start the Streamlit website in the foreground
streamlit run app.py --server.port $PORT --server.address 0.0.0.0
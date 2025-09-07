# Import the userbot and bot clients along with the bot token
from clients import crowthon, crowthon_bot, token

# Import glob to dynamically load plugin files
from glob import glob

# Import asyncio utilities for asynchronous operations
from asyncio import sleep, run

# Import signal handling for graceful shutdown
from signal import signal, SIGINT

# Import functions to handle file paths
from os.path import abspath, join, dirname

# Import the sys module to modify the Python module search path
import sys

# For easy and cross-platform path handling
from pathlib import Path

# Import environment variable
from os import environ

# Get the absolute path of the project root directory
base_dir = abspath(join(dirname(__file__), ".."))

# Add the project root to the beginning of sys.path to enable module imports
sys.path.insert(0, base_dir)

# Define a function to handle termination signals (e.g., Ctrl+C)
def signal_handler(sig, frame):
    print("\nReceived signal:", sig)
    print("Stopping Crowthon gracefully...")
    crowthon.disconnect() # Disconnect the userbot client
    crowthon_bot.disconnect() # Disconnect the bot client
    exit(0)

# Register the signal handler for SIGINT (Ctrl+C)
signal(SIGINT, signal_handler)

# Define the main asynchronous function that runs the userbot and bot
async def main():
    # Dynamically load all plugin files from the plugins directory
    for plugin_path in glob("crowthon/plugins/*.py"):
        plugin_name = Path(plugin_path).stem
        module = __import__(f"crowthon.plugins.{plugin_name}", fromlist=[plugin_name])

        # If the plugin has a load_plugin coroutine, load it
        if hasattr(module, "load_plugin"):
            await module.load_plugin(crowthon)
            print(f"{plugin_name} plugin loaded successfully")
    try:
        # Start the userbot client
        await crowthon.start()
        print("Crowthon started successfully")

        # Start the bot client with the provided token
        await crowthon_bot.start(bot_token=token)
        print("Assistant Bot started successfully\n\n")

        # Check if the environment variable 'render' is set to 'true'
        # This indicates that the project is running on the Render platform
        if environ.get("render") == "true":
            # Import and run the dummy web server to keep the service alive on Render
            from server import keep_alive
            keep_alive()

        # Keep the program running indefinitely
        await sleep(float("inf"))
    except KeyboardInterrupt:
        # Handle Ctrl+C interruption and disconnect clients
        print("\nKeyboardInterrupt received. Stopping Crowthon gracefully...")
        await crowthon.disconnect()

# Run the main coroutine using asyncio's event loop
run(main())

import os
import threading
from flask import Flask
from pyrogram import Client

# ---- Yaha apka usertagger bot ka pura code hoga ----
# Example:
app_bot = Client(
    "usertagger",
    api_id=int(os.environ["API_ID"]),
    api_hash=os.environ["API_HASH"],
    bot_token=os.environ["BOT_TOKEN"]
)

# Flask server
app = Flask(__name__)

@app.route("/")
def home():
    return "Usertagger Bot is Running on Render!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    # Flask ko alag thread me run karo
    threading.Thread(target=run_flask).start()
    
    # Telegram bot start karo
    app_bot.run()

import os
import discord
from discord.ext import commands
from flask import Flask, request, jsonify
import asyncio
import threading

# --- CONFIGURATION (CHANGE THESE NUMBERS) ---
# Paste your Discord Channel ID below (Replace the 0 with your number)
TARGET_CHANNEL_ID = 0  

# Paste your Discord User ID below (Replace the 0 with your number)
YOUR_DISCORD_ID = 0    
# --------------------------------------------

# 1. SETUP THE WEB SERVER TO RECEIVE EGG DATA FROM ROBLOX
app = Flask('')
bot_instance = None

@app.route('/egg_spawn', methods=['POST'])
def egg_spawn():
    data = request.json or {}
    egg_name = data.get('egg_name', 'Unknown Egg')
    rarity = data.get('rarity', 'Secret')
    
    if bot_instance and bot_instance.is_ready():
        # Safely send the message from the web server thread to Discord
        asyncio.run_coroutine_threadsafe(
            send_egg_alert(egg_name, rarity), 
            bot_instance.loop
        )
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "bot_not_ready"}), 500

async def send_egg_alert(egg_name, rarity):
    channel = bot_instance.get_channel(TARGET_CHANNEL_ID)
    if channel:
        # This sends the message and pings your specific account
        await channel.send(f"🚨 **GLOBAL SPAWN ALERT!** 🚨\n<@{YOUR_DISCORD_ID}> A **{rarity}** egg (**{egg_name}**) has just spawned globally!")

def run_web_server():
    # Runs the web server on port 8080
    app.run(host='0.0.0.0', port=8080)

# 2. SETUP THE DISCORD BOT
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    global bot_instance
    bot_instance = bot
    print(f'Bot is online as {bot.user}')

# 3. START BOTH SERVICES TOGETHER
if __name__ == "__main__":
    # Start the web server in a background thread
    server_thread = threading.Thread(target=run_web_server)
    server_thread.daemon = True
    server_thread.start()
    
    # Securely logs in using the DISCORD_TOKEN environment variable from Render
    bot.run(os.environ.get('DISCORD_TOKEN'))

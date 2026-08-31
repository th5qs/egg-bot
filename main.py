import os
import discord
from discord.ext import commands
from flask import Flask, request, jsonify
import asyncio
import threading

# --- CONFIGURATION ---
# REPLACE THE 0 BELOW WITH YOUR DISCORD CHANNEL ID
TARGET_CHANNEL_ID = 1128792389813817519  

# YOUR DISCORD USER ID (ALREADY ADDED FOR YOU)
YOUR_DISCORD_ID = 898258858458382417    
# --------------------------------------------

app = Flask('')
bot_instance = None

# Automated Web Receiver for your Roblox Executor
@app.route('/egg_spawn', methods=['POST'])
def egg_spawn():
    data = request.json or {}
    message_text = data.get('message', 'An egg spawned!')
    
    if bot_instance and bot_instance.is_ready():
        asyncio.run_coroutine_threadsafe(
            send_automated_alert(message_text), 
            bot_instance.loop
        )
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "bot_not_ready"}), 500

async def send_automated_alert(text):
    channel = bot_instance.get_channel(TARGET_CHANNEL_ID)
    if channel:
        embed = discord.Embed(
            title="🚨 AUTOMATED GLOBAL EGG SPAWN! 🚨",
            description=f"**Notification detected:**\n`{text}`",
            color=discord.Color.gold()
        )
        embed.set_footer(text="Steal an Egg Live Capture")
        await channel.send(content=f"<@{YOUR_DISCORD_ID}>", embed=embed)

# Discord command (Backup)
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    global bot_instance
    bot_instance = bot
    print(f'Bot is online as {bot.user}')

@bot.command()
async def egg(ctx, rarity: str, *, egg_name: str):
    if ctx.channel.id == TARGET_CHANNEL_ID:
        await ctx.message.delete()
        embed = discord.Embed(title="🚨 MANUAL EGG ALERT! 🚨", description=f"A **{rarity.upper()}** egg ({egg_name}) has spawned!", color=discord.Color.red())
        await ctx.send(content=f"<@{YOUR_DISCORD_ID}>", embed=embed)

def run_web_server():
    app.run(host='0.0.0.0', port=8080)

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_web_server)
    server_thread.daemon = True
    server_thread.start()
    bot.run(os.environ.get('DISCORD_TOKEN'))


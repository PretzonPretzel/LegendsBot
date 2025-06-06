import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio  # for non-blocking sleeps

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.command(name="ping", help="Ping the bot, ensuring it's alive")
async def ping(ctx):
    await ctx.reply("KAMEHAMEHA! Pong :3c")

@bot.event
async def on_message(message):
    # 1) Ignore bots (including yourself)
    if message.author.bot:
        return

    content = message.content.lower()

    # 2) "limits" trigger
    if "limits" in content:
        await message.reply("WE SAIYANS HAVE NO LIMITS!")
        await asyncio.sleep(1)
        await message.reply("LETS CHARGE TOGETHER AT FULL POWER.")
        await asyncio.sleep(0.25)
        await message.reply(
            "https://tenor.com/view/we-saiyans-have-no-limits-dokkan-dragon-ball-super-goku-vegeta-gif-3202169445918711234"
        )

    # 3) "17" trigger
    if "17" in content:
        await message.reply("NOBODY CAN BEAT ME WHEN I'M SUPER 17!")
        await asyncio.sleep(1)
        await message.reply("https://25.media.tumblr.com/42d5657a812999271746a168a21e5c60/tumblr_mfx1odGjeK1s02vreo1_r1_500.gif")

    # 4) "Gogeta" trigger
    if "futile" in content:
        await message.reply("ITS FUTILE!")
        await message.reply(file=discord.File("/Users/pretzon/Documents/GitHub/LegendsBot/Gogeta Status. [Green Screen] - NotANamekian (1080p, h264).mp4"))
        
        
    # 4) Finally, allow other commands to run
    await bot.process_commands(message)

bot.run(token)

import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import time
load_dotenv()

token = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent
intents.members = True  # Enable member intent for member-related commands

bot = commands.Bot(intents=intents)


async def on_message(self, message):
    if message.content.contains("Limits") or message.content.contains("limits"):
        await self.reply(f"WE SAIYANS HAVE NO LIMITS!")
        time.sleep(1)
        await self.reply("LETS CHARGE TOGETHER AT FULL POWER.")
        await self.reply("https://tenor.com/view/we-saiyans-have-no-limits-dokkan-dragon-ball-super-goku-vegeta-gif-3202169445918711234")
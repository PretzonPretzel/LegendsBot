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
        await message.reply(file=discord.File("/videos/Gogeta Status. [Green Screen] - NotANamekian (1080p, h264).mp4"))
    
    # 5) "Zamasu" trigger
    if "pure" in content:
        await message.reply("I am justice given form! I am the world! Now venerate the most noble, most splendid, immortal, and supremely powerful god: Zamasu! This day marks the beginning of a new chapter of the universe! The name of the one to author that chapter is Zamasu, the bringer of eternal order! No matter how much mortals combine their power, it will be nothing more than child's play compared to the power of the gods! To think you can touch a god proves that you are stained with sin! Once again mortals imitate the gods, as they always do... And why is that? Because the gods are great? Because the gods are too beautiful? But is it sad? Are mortals to be pitied? An act committed by the gods is virtuous, but the same act committed by a mortal is evil...and thus becomes a sin! Listen well Saiyan... Goku... Although you are a mortal, you have attained the power of the gods... I suppose I should commend your perseverance in the face of your annihilation... I shall defeat you, eradicate humanity, and bring about the dawn of an endless age that can never be tainted. You are a monument to the failure of the gods who created this universe! There is no longer a need for Supreme Kais or Gods of Destruction! I, Zamasu, will purify this world. Behold the power of the gods! Behold! A body with limitless power and immortality! Indeed, by becoming one with Goku, I have taken the sins of humanity and the failure of the gods into myself! The time has come to open the earth and wash everything away... Rejoice, for the world of the gods is at hand! This tainted world is about to come to an end... A foolish lifeform doomed to see its very own mistakes. So, where will you go for aid now? The past? The future?")
        await asyncio.sleep(1)
        await message.reply("https://tenor.com/view/zamasu-gods-dokkan-dbz-dbs-gif-14684682158021936799")
        
        
    # 6) "Trunks" trigger
    if "android" in content:
        await message.reply(file=discord.File("/videos/If They Set That Android Free It Will Be The End Of All Of Us - Trunks Loses It - DBZ Dragon Ball Z - DBZMusicFanHD (360p, h264).mp4"))    
    
    if "future" in content:
        await message.reply(file=discord.File("/videos/＂THIS IS FOR GOHAN!＂ - LAiB_Gaming (1080p, h264) (online-video-cutter.com)(1).mp4"))
    
    # 7) "Piccolo" trigger
    if "win" in content:
        await message.reply("# **I CAN WIN. I FEEL GREAT. I. CAN. DO. THIS.**")
        asyncio.sleep(1)
        await message.reply(file=discord.File("/videos/I FEEL GREAT. I CAN WIN. I. CAN. DO. THIS. - mattheavel (480p, h264) (online-video-cutter.com).mp4"))
    
    # Finally, allow other commands to run
    await bot.process_commands(message)

bot.run(token)

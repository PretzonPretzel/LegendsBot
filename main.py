import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio  # for non-blocking sleeps
import webserver
import random

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

memes = False #CHANGE LATER TO TRUE TO ENABLE MEMES

@bot.command(name="ping", help="Ping the bot, ensuring it's alive")
async def ping(ctx):
    await ctx.reply("KAMEHAMEHA! Pong :3c")

@bot.command(name="memes-enable", help="Turn chat reactions ON")
async def memes_enable(ctx):
    global memes
    memes = True
    await ctx.reply("Chat reactions ENABLED 👍")

@bot.command(name="memes-disable", help="Turn chat reactions OFF")
async def memes_disable(ctx):
    global memes
    memes = False
    await ctx.reply("Chat reactions DISABLED 👎")

@bot.command(name="sick_em", help="Sick him, bot!")
async def sick_him(ctx):
    await ctx.send("BARK BARK BARK")
    await ctx.send("https://tenor.com/view/girl-jumping-around-like-a-wolf-gif-26759976")

@bot.command(name="fuckem", help="Kills whomever you want")
async def fuck_em(ctx, member: commands.MemberConverter):
    attack = random.randint(1, 15)
    fucker = ctx.author.display_name
    fuckee = member.display_name
    
    if attack == 1: #kamehameha attack
        await ctx.send("KAAAAMEEEEE")
        await asyncio.sleep(0.9)
        await ctx.send("HAAAAMEEEEEE")
        await asyncio.sleep(0.9)
        await ctx.send("# **HAAAAAAAAAAAAAA**")
        await asyncio.sleep(0.5)
        await ctx.send("https://i.pinimg.com/originals/31/37/89/3137899f774569326119b5992d3a4409.gif")
    
    elif attack == 2: #final flash attack
        vegetGif = random.randint(1,2)
        await ctx.send(f"YOU COCKY BASTARD. ARE YOU BRAVE ENOUGH TO TAKE THIS ONE, {fuckee.upper()}?!")
        await asyncio.sleep(1.2)
        await ctx.send(f"FINALLLLL")
        await asyncio.sleep(0.9)
        await ctx.send(f"# **FLASHHHHHHH**")
        await asyncio.sleep(0.5)
        if vegetGif == 1:
            await ctx.send("https://i.pinimg.com/originals/89/fb/05/89fb055e736889c54778fa9348c2f0e6.gif")
        elif vegetGif == 2:
            await ctx.send("https://cdn.discordapp.com/attachments/1380198124081119435/1381662696625143919/0a12d9726479da1c6b3ab9ac9e4d044c.gif?ex=68485528&is=684703a8&hm=a84ed39da231d0ae3556ee20e0642f8d1c7b4f64dfdd15afa07e3951d9ebc24b&")
    
    elif attack == 3: #i am atomic attack
        await ctx.send(f"I am...")
        await asyncio.sleep(1)
        await ctx.send(f"## **Atomic.**")
        await asyncio.sleep(0.5)
        await ctx.send(f"https://cdn.discordapp.com/attachments/1380198124081119435/1381662788023226418/forcegate1.gif?ex=6848553e&is=684703be&hm=b2a2ebbbcfdbab30d91edb9a4b47df8f2fd588f1508d34142db3844b1a08d816&")
        
    elif attack == 4: #domain expansion attack
        domain = random.randint(1,4)
        await ctx.send(f"Domain Expansion...")
        await asyncio.sleep(0.8)
        
        if domain == 1:
            await ctx.send(f"# **Infinite Void**")
            await asyncio.sleep(0.5)
            await ctx.send(f"https://cdn.discordapp.com/attachments/1380198124081119435/1381663168165838858/domain-expansion.gif?ex=68485599&is=68470419&hm=9a5b28490f449f395d46fc988a1f1ba5d8d20e642d620e31848bce28e8ef3689&")
        elif domain == 2:
            await ctx.send(f"# **Malevolent Shrine**")
            await asyncio.sleep(0.5)
            await ctx.send(f"https://media.discordapp.net/attachments/1380198124081119435/1381663168560107550/sukuna-mahoraga.gif?ex=68485599&is=68470419&hm=6d0e4649efaaf6a783d319132af132d27206989f53c127e53042b455f04ab2d2&=&width=996&height=446")
        elif domain == 3:
            await ctx.send(f"# **Self Embodiment of Perfection**")
            await asyncio.sleep(0.5)
            await ctx.send(f"https://media.discordapp.net/attachments/1380198124081119435/1381663169042186240/jjk-jujutsu-kaisen.gif?ex=68485599&is=68470419&hm=1214cafadc08226374d5ebfe470a36ec9e936285ab7d3738260ac3fe1b748bff&=&width=996&height=562")
        elif domain == 4:
            await ctx.send(f"# **Chimera Shadow Garden**")
            await asyncio.sleep(0.5)
            await ctx.send(f"https://media.discordapp.net/attachments/1380198124081119435/1381663169423999136/megumi-fushiguro-megumi-domain-expansion.gif?ex=68485599&is=68470419&hm=b5cec5b9949ecf3eb1d42e8a855740c6fb81ba53a5a7cc48089fb5bba271efe0&=&width=996&height=562")

    elif attack == 5: #hollow purple attack
        await ctx.send("Nine Ropes, Polarized Light, Crow and Declaration, Between Front and Back...")
        await asyncio.sleep(0.9)
        await ctx.send(f"## **Hollow Purple**")
        await asyncio.sleep(0.5)
        await ctx.send(f"https://media.discordapp.net/attachments/1380198124081119435/1381663464073728130/gojo-gojo-satoru.gif?ex=684855df&is=6847045f&hm=3954f92f96123a0ceeb8fb4d24b8a57906aa925ea4738f469d59760a530a2d3d&=&width=996&height=456")

    elif attack == 6: #blash flash attack
        blackflash = random.randint(1,6)
        await ctx.send(f"The sparks of black do not choose who to bless, {fuckee}.")
        await asyncio.sleep(1.2)
        await ctx.send(f"# **Black Flash**")
        await asyncio.sleep(0.5)
        if blackflash == 1:
            await ctx.send("https://cdn.discordapp.com/attachments/1380198124081119435/1381663696975298620/jjk-jjk-s2.gif?ex=68485617&is=68470497&hm=07986931101f68c41596588e08583f9a024d0231634c4f25a31b526cb8e7668f&")
        elif blackflash == 2:
            await ctx.send("https://cdn.discordapp.com/attachments/1380198124081119435/1381663697444802714/jujutsu-kaisen-jujutsu-kaisen-season-2.gif?ex=68485617&is=68470497&hm=0859c4581e7fd576a70763a3b129bb554934c07750128f5991b68ec554ed4644&")
        elif blackflash == 3:
            await ctx.send("https://media.discordapp.net/attachments/1380198124081119435/1381663697843392583/black-flash-jujutsu-kaisen.gif?ex=68485617&is=68470497&hm=67332fae0410cfd2a703abd0678425a7a308446e6ddfed0eaf7bbd0cd01eb6b0&=&width=1280&height=720")
        elif blackflash == 4:
            await ctx.send("https://media.discordapp.net/attachments/1380198124081119435/1381663698162286693/jjk-jujutsu-kaisen_1.gif?ex=68485617&is=68470497&hm=74fd2c54cb1c809dd96a0219205e9d81c35f07e4a9b2ffbc784162a3c76bb15a&=&width=996&height=562")
        elif blackflash == 5:
            await ctx.send("https://media.discordapp.net/attachments/1380198124081119435/1381663698682122512/jujutsu-kaisen-itadori-yuuji.gif?ex=68485617&is=68470497&hm=a3fc0b8ba474d780f59e7231347aed81855242d194ad1cb25ab690298b2b2b36&=&width=1280&height=852")
        elif blackflash == 6:
            await ctx.send("https://media.discordapp.net/attachments/1380198124081119435/1381663699139559555/itadori-yuji-kugisaki-nobara.gif?ex=68485617&is=68470497&hm=714b38297bd84bed95394bf42c9ba49fdfcbb38cd2485150e2b738fbfcb01bb3&=&width=996&height=556")

    elif attack == 7: #serious series attack
        series = random.randint(1,2)
        await ctx.send(f"Serious series...")
        await asyncio.sleep(1.2)
        if series == 1:
            await ctx.send(f"# **Serious Punch**")
            await asyncio.sleep(0.5)
            await ctx.send(f"https://media.discordapp.net/attachments/1380198124081119435/1381660383927992390/saitama-serious-vs.gif?ex=68485301&is=68470181&hm=5e56c4f90ffffc4a182aabae9c39fb123250654d031ada0d3dc0c5f238bf8b8a&=&width=996&height=562")
        elif series == 2:
            await ctx.send(f"# **Serious Tableflip**")
            await asyncio.sleep(0.5)
            await ctx.send(f"https://media.discordapp.net/attachments/1380198124081119435/1381660383462428863/saitama-serious-vs-cosmic-garou-serious-series.gif?ex=68485301&is=68470181&hm=c73130b3f9b7616ca568774fa489c15e88b893fb9d6874c6dffcad27fda6ce54&=&width=748&height=422")

    elif attack == 8: #hakai attack
        hakai = random.randint(1,2)
        await ctx.send(f"Sorry, {member.display_name}, but your luck has run out.")
        await asyncio.sleep(1.7)
        await ctx.send(f"# **Hakai.**")
        await asyncio.sleep(0.5)
        if hakai == 1:
            await ctx.send("https://cdn.discordapp.com/attachments/1380198124081119435/1381659253332512908/voce-usou-hankai.gif?ex=684851f3&is=68470073&hm=5757914c5e4a196c8e62f52ee35a3581c199a90c0336cb7caa6b4f379bdb47ee&")
        elif hakai == 2:
            await ctx.send("https://media.discordapp.net/attachments/1380198124081119435/1381659252946370730/goku-manga-hakai-hakai.gif?ex=684851f3&is=68470073&hm=59775cb6f7cfa58d9bf579a77c2cdedea4f295007c71721d80c826f75e176a2c&=&width=996&height=560")

    elif attack == 9: #soul punisher attack
        soulPunisher = random.randint(1,2)
        humans = [m for m in ctx.guild.members if not m.bot and m != ctx.author]
        member1 = random.choice(humans)
        member2 = random.choice(humans)
        await ctx.send(f"I am not *{member1.display_name}* or *{member2.display_name}*! I am **{fucker}**! It's over {fuckee}, I've come for you!")
        await asyncio.sleep(1.5)
        await ctx.send(f"Every force you create has an echo. Your own bad energy will be your undoing!")
        await asyncio.sleep(0.5)
        if soulPunisher == 1:
            await ctx.send(f"https://i.makeagif.com/media/4-15-2022/1oo8uC.gif")
        elif soulPunisher == 2:
            await ctx.send(f"https://i.pinimg.com/originals/f0/b4/77/f0b477f65deb1fca584efdb5542e665b.gif")

    elif attack == 10: #spirit bomb attack
        spiritbomb = random.randint(1,3)
        textMsg = await ctx.send(f"Everyone! I need you all to lend me your energy!")
        gifMsg = await ctx.send("https://media.tenor.com/8Ltt65SLeFUAAAAM/genki-dama-spirit-bomb.gif")
        await asyncio.sleep(4)
        
        await textMsg.edit(content=f"IT'S READY!")
        await gifMsg.edit(content="https://miro.medium.com/v2/resize:fit:884/1*ZTUASIVTMSDYY7K4ZSq98g.gif")
        
        await asyncio.sleep(3)

        await textMsg.edit(content=f"# **TAKE THIS!**")
        await asyncio.sleep(0.5)
        if spiritbomb == 1:
            await gifMsg.edit(content="https://media.discordapp.net/attachments/1380198124081119435/1381660256123224124/goku.gif?ex=684852e3&is=68470163&hm=b15c1caed68b90669825aa83a92071fce206fdc0f8924598fd4fa918063cec8e&=&width=1280&height=720")
        elif spiritbomb == 2:
            await gifMsg.edit(content="https://media.discordapp.net/attachments/1380198124081119435/1381660256827998208/dragon-ball-z-one-piece.gif?ex=684852e3&is=68470163&hm=e1e1167e26a19f4a337e4f038eaa5abb915ef1fd7c39b61bcf8aa9bdc04c58fd&=&width=748&height=422")
        elif spiritbomb == 3:
            await gifMsg.edit(content="https://media.discordapp.net/attachments/1380198124081119435/1381660257230786711/goku-genkidama.gif?ex=684852e3&is=68470163&hm=91f1531f694f51aee054aed5592a263f68604bef666930af08ad9bb0596ccba6&=&width=746&height=562")

    elif attack == 11: #rasengan attack
        await ctx.send(f"# **Rasengan!**")
        await asyncio.sleep(0.5)
        await ctx.send("https://media.discordapp.net/attachments/1380198124081119435/1381658129766289539/minato.gif?ex=684850e8&is=6846ff68&hm=c29b72691cfe8e4914d105998b3dd1da8f22b80cbe5d14608949c15eadf5d0c0&=&width=996&height=592")

    elif attack == 12: #getsuga attack
        await ctx.send(f"Getsuga....")
        await asyncio.sleep(0.9)
        await ctx.send(f"# **Tensho!**")
        await asyncio.sleep(0.5)
        await ctx.send("https://cdn.discordapp.com/attachments/1380198124081119435/1381659616487804988/ichigo-kurosaki-ichigo.gif?ex=6848524a&is=684700ca&hm=41538f4748df2d9b2188b9adaace917476e11f8e1fdbd18a887e55e5178a2b6e&")

    elif attack == 13: #invincible beatdown
        titlecard = random.randint(1,2)
        await ctx.send(f"Is this what you wanted, {fuckee}?")
        await asyncio.sleep(1)
        await ctx.send(f"You enjoy yourself?")
        await asyncio.sleep(1.5)
        await ctx.send(f"STILL HAVING FUN?")
        await asyncio.sleep(1.3)
        await ctx.send(f"**ANSWER ME!**")
        await asyncio.sleep(1.2)

        webhooks = await ctx.channel.webhooks()
        webhook = discord.utils.get(webhooks, name="Impersonator")
        if webhook is None:
            webhook = await ctx.channel.create_webhook(name="Impersonator")
            
        await webhook.send(
            content="I take the good with the bad.",
            username=member.display_name,
            avatar_url=member.display_avatar.url
        )
        await webhook.delete()
        
        await asyncio.sleep(1.5)
        await ctx.send("# **GRAAAAAAHHHHHH**")
        await asyncio.sleep(0.5)
        if titlecard == 1:
            await ctx.send("https://media.discordapp.net/attachments/1380198124081119435/1381656268032315533/invincible-punch-invincible.gif?ex=68484f2c&is=6846fdac&hm=7ffef3dccbe7001154d01007ad17cf29b1f245770091690f8c2e119a5c1be711&=&width=996&height=562")
        elif titlecard == 2:
            await ctx.send("https://preview.redd.it/characters-using-their-head-btw-congrats-to-the-sub-for-100k-v0-fvupe2avvgoe1.gif?width=640&crop=smart&auto=webp&s=0d80ce208df2ed15738d51a91211ac9e71b61894")
        
    elif attack == 14: #bat lol
        await ctx.send(f"https://tenor.com/view/the-shusher-bat-staff-rod-gif-8855179341029231927")
        await ctx.send("https://youtu.be/f8mL0_4GeV0?si=r5U5AsQ74Mv4M5ZK")

    elif attack == 15: #failure
        webhooks = await ctx.channel.webhooks()
        webhook = discord.utils.get(webhooks, name="Impersonator")
        if webhook is None:
            webhook = await ctx.channel.create_webhook(name="Impersonator")
        
        await webhook.send(
            content=f"Wha- What the?!",
            username=ctx.author.display_name,
            avatar_url=ctx.author.display_avatar.url
        )
        await asyncio.sleep(0.2)
        await webhook.send(
            content=f"https://i.makeagif.com/media/1-28-2019/P8wA11.gif",
            username=ctx.author.display_name,
            avatar_url=ctx.author.display_avatar.url
        )
        
        await asyncio.sleep(1.5)
        await webhook.send(
            content=f"Now what was that supposed to be, {fucker}?",
            username=member.display_name,
            avatar_url=member.display_avatar.url
        )
        await asyncio.sleep(0.9)
        await webhook.send(
            content=f"https://media.discordapp.net/attachments/1380188830753362063/1381724686966198423/broly-goku.gif?ex=68488ee4&is=68473d64&hm=805aa23a2012f24a5a390f2e767d42926553893612980c409e55f8b4e2647f19&=&width=1280&height=892",
            username=member.display_name,
            avatar_url=member.display_avatar.url
        )
        
        await asyncio.sleep(1.5)
        await webhook.send(
            content=f"https://media.discordapp.net/attachments/1380188830753362063/1381724687528230972/broly-vs-goku-broly.gif?ex=68488ee4&is=68473d64&hm=1724cdfeaa0917d6977c38659256396cf0be0658666e16866675ef6a83e35439&=&width=996&height=926",
            username=member.display_name,
            avatar_url=member.display_avatar.url
        )

        await webhook.delete()


@bot.event
async def on_message(message):
    # 1) Ignore bots (including yourself)
    if message.author.bot:
        return
    
    await bot.process_commands(message)
    
    if memes == False:
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
        await message.reply(file=discord.File("videos/Gogeta Status. [Green Screen] - NotANamekian (1080p, h264).mp4"))
    
    # 5) "Zamasu" trigger
    if "pure" in content:
        await message.reply("I am justice given form! I am the world! Now venerate the most noble, most splendid, immortal, and supremely powerful god: Zamasu! This day marks the beginning of a new chapter of the universe! The name of the one to author that chapter is Zamasu, the bringer of eternal order! No matter how much mortals combine their power, it will be nothing more than child's play compared to the power of the gods! To think you can touch a god proves that you are stained with sin! Once again mortals imitate the gods, as they always do... And why is that? Because the gods are great? Because the gods are too beautiful? But is it sad? Are mortals to be pitied? An act committed by the gods is virtuous, but the same act committed by a mortal is evil...and thus becomes a sin! Listen well Saiyan... Goku... Although you are a mortal, you have attained the power of the gods... I suppose I should commend your perseverance in the face of your annihilation... I shall defeat you, eradicate humanity, and bring about the dawn of an endless age that can never be tainted. You are a monument to the failure of the gods who created this universe! There is no longer a need for Supreme Kais or Gods of Destruction! I, Zamasu, will purify this world. Behold the power of the gods! Behold! A body with limitless power and immortality! Indeed, by becoming one with Goku, I have taken the sins of humanity and the failure of the gods into myself! The time has come to open the earth and wash everything away... Rejoice, for the world of the gods is at hand! This tainted world is about to come to an end... A foolish lifeform doomed to see its very own mistakes. So, where will you go for aid now? The past? The future?")
        await asyncio.sleep(1)
        await message.reply("https://tenor.com/view/zamasu-gods-dokkan-dbz-dbs-gif-14684682158021936799")
        
        
    # 6) "Trunks" trigger
    if "android" in content:
        await message.reply(file=discord.File("videos/If They Set That Android Free It Will Be The End Of All Of Us - Trunks Loses It - DBZ Dragon Ball Z - DBZMusicFanHD (360p, h264).mp4"))    
    
    if "future" in content:
        await message.reply(file=discord.File("videos/＂THIS IS FOR GOHAN!＂ - LAiB_Gaming (1080p, h264) (online-video-cutter.com)(1).mp4"))
    
    # 7) "Piccolo" trigger
    if "win" in content:
        await message.reply("# **I CAN WIN. I FEEL GREAT. I. CAN. DO. THIS.**")
        asyncio.sleep(1)
        await message.reply(file=discord.File("videos/I FEEL GREAT. I CAN WIN. I. CAN. DO. THIS. - mattheavel (480p, h264) (online-video-cutter.com).mp4"))
    
@bot.event
async def Load():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')
            
async def main():
    async with bot:
        await Load()
        #webserver.keep_alive()  # Start the web server to keep the bot alive
        await bot.start(token)

asyncio.run(main())
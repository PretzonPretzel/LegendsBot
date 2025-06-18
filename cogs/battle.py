# battle.py
import random
import discord
from discord.ext import commands
import asyncio
import json
import os

# ─── Wins File ───────────────────────────────────────────────────────────────────
WINS_FILE = "wins.json"

def load_wins() -> dict[str, int]:
    if os.path.exists(WINS_FILE):
        with open(WINS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_wins(wins: dict[str, int]):
    with open(WINS_FILE, "w") as f:
        json.dump(wins, f)

# ─── Player ───────────────────────────────────────────────────────────────────
class Player:
    def __init__(self, member: discord.Member):
        self.member = member
        self.hp     = 100

    @property
    def name(self) -> str:
        return self.member.display_name

# ─── Session ──────────────────────────────────────────────────────────────────
class Session:
    def __init__(self, p1: Player, p2: Player, channel: discord.TextChannel):
        self.fucker       = p1               # challenger
        self.fucked       = p2               # challenged
        self.turn         = p1               # who goes first
        self.channel      = channel
        self.in_progress  = False            # flips on Accept
        self.pending_beam: tuple[Player, Attack] | None = None # Player who fired a beam last
        self.pending_special: tuple[Player, Attack] | None = None
        
        
    def other(self, player: Player) -> Player:
        return self.fucked if player is self.fucker else self.fucker

    def is_over(self) -> bool:
        return self.fucker.hp <= 0 or self.fucked.hp <= 0

    def winner(self) -> Player:
        return self.fucker if self.fucked.hp <= 0 else self.fucked

# ─── Attack Definitions ───────────────────────────────────────────────────────
from enum import Enum, auto
from dataclasses import dataclass

class AttackType(Enum):
    STRIKE   = auto()
    BEAM     = auto()
    SPECIAL  = auto()
    INSTANT  = auto()
    BACKFIRE = auto()

@dataclass
class Attack:
    id:   int
    name: str
    type: AttackType

# fill in your real names if you like
ALL_ATTACKS = {
    1:  Attack(1,  "Kamehameha",          AttackType.BEAM),
    2:  Attack(2,  "Final Flash",         AttackType.BEAM),
    3:  Attack(3,  "Invincible Beatdown", AttackType.STRIKE),
    4:  Attack(4,  "I Am Atomic",         AttackType.SPECIAL),
    5:  Attack(5,  "Spirit Bomb",         AttackType.BEAM),
    6:  Attack(6,  "Black Flash",         AttackType.STRIKE),
    7:  Attack(7,  "Serious Series",      AttackType.STRIKE),
    8:  Attack(8,  "Hakai",               AttackType.INSTANT),
    9:  Attack(9,  "Soul Punisher",       AttackType.INSTANT),
   10:  Attack(10, "Rasengan",            AttackType.STRIKE),
   11:  Attack(11, "Getsuga Tensho",      AttackType.BEAM),
   12:  Attack(12, "Domain Expansion",    AttackType.SPECIAL),
   13:  Attack(13, "Bat Whack",           AttackType.SPECIAL),
   14:  Attack(14, "Broly Backfire",      AttackType.BACKFIRE),
   15:  Attack(15, "Hollow Purple",       AttackType.BEAM),
   16:  Attack(16, "Galick Gun",          AttackType.BEAM),
}

# sets for quick type checks
STRIKES   = {a.id for a in ALL_ATTACKS.values() if a.type is AttackType.STRIKE}
BEAMS     = {a.id for a in ALL_ATTACKS.values() if a.type is AttackType.BEAM}
SPECIALS  = {a.id for a in ALL_ATTACKS.values() if a.type is AttackType.SPECIAL}
INSTANTS  = {a.id for a in ALL_ATTACKS.values() if a.type is AttackType.INSTANT}
BACKFIRES = {a.id for a in ALL_ATTACKS.values() if a.type is AttackType.BACKFIRE}

# ─── Challenge UI ─────────────────────────────────────────────────────────────
class ChallengeView(discord.ui.View):
    def __init__(self, session: Session, sessions: dict[int, Session]):
        super().__init__(timeout=30.0)
        self.session  = session
        self.sessions = sessions
        self.message: discord.Message | None = None

    async def on_timeout(self):
        if not self.session.in_progress:
            await self.message.edit(
                content="⏰ Challenge timed out. Looks like they ran away, haha!",
                view=None
            )
            self.sessions.pop(self.session.channel.id, None)

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.success)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.session.fucked.member:
            return await interaction.response.send_message("You can’t accept this!", ephemeral=True)
        self.session.in_progress = True
        await interaction.response.edit_message(
            content=(
                f"⚔️ **Battle Start!**\n"
                f"{self.session.fucker.name} vs {self.session.fucked.name}\n"
                f"**{self.session.turn.name}** goes first—use `!roll` or `!r`!\n\n"
                f"-# You can use `!end` at any time to end the fight early. You aren't a bitch though, are you?"
            ),
            view=None
        )

    @discord.ui.button(label="Deny", style=discord.ButtonStyle.danger)
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.session.fucked.member:
            return await interaction.response.send_message("You can’t deny this!", ephemeral=True)
        insults = ["Weak ass mf.", "You a bitch fr.", "Coward.", "Pathetic.", "Filthy monkey...can't even fight back.", "Are you trembling?", "Too much of a power gap, huh?", "What's wrong? Feeling chickenshit?", "Oh. Well, since they declined & i have your attention, did you know that The FitnessGram Pacer Test is a multistage aerobic capacity test that progressively gets more difficult as it continues. The 20 meter pacer test will begin in 30 seconds. Line up at the start. The running speed starts slowly but gets faster each minute after you hear this signal bodeboop. A sing lap should be completed every time you hear this sound. ding. Remember to run in a straight line and run as long as possible. The second time you fail to complete a lap before the sound, your test is over. The test will begin on the word start. On your mark. Get ready!… Start! ding"]
        await interaction.response.edit_message(
            content=f"{interaction.user.mention} denies the fight. {random.choice(insults)}",
            view=None
        )
        self.sessions.pop(self.session.channel.id, None)

# ─── The Battle Cog ───────────────────────────────────────────────────────────
class Battle(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.sessions: dict[int, Session] = {}
        self.wins: dict[str, int] = load_wins()
        
    def record_win(self, user: discord.Member):
        uid = str(user.id)
        self.wins[uid] = self.wins.get(uid, 0) + 1
        save_wins(self.wins)

    @commands.command(name="challenge", aliases=["c"], help="Invite someone to a 1v1 fight")
    async def challenge(self, ctx, opponent: discord.Member):
        if ctx.channel.id in self.sessions:
            return await ctx.send("🚫 A battle is already in progress! Fucking wait.")
        if opponent == ctx.author:
            return await ctx.send("You can’t battle yourself!")

        p1 = Player(ctx.author)
        p2 = Player(opponent)
        session = Session(p1, p2, ctx.channel)
        self.sessions[ctx.channel.id] = session

        view = ChallengeView(session, self.sessions)
        msg  = await ctx.send(
            f"{opponent.mention}, you’ve been challenged by **{ctx.author.display_name}**! ",
            view=view
        )
        view.message = msg

    @commands.command(name="roll", aliases=["r"], help="Roll your attack")
    async def roll(self, ctx):
        session = self.sessions.get(ctx.channel.id)
        if not session or not session.in_progress:
            return await ctx.send("❓ Are you stupid? Start a fight to roll, fuckass.")
        attacker = session.turn
        if ctx.author != attacker.member:
            return await ctx.send(f"⌛ Wait your fucking turn—it's {attacker.name}'s.")
        
        # **Prevent a new roll if you must stick/reroll a pending special**
        if session.pending_special:
            return await ctx.send(
                f"🌀 You rolled a special earlier! "
                "Type `!stick` or `!s` to lock it in or `!reroll` to roll again."
            )

        # 1) pick your attack
        attack_id = random.randint(1, 16)
        
        # Uncomment and change number to select attack and debug events
        #attack_id = 1
        #options = [5, 10]
        #attack_id = random.choice(options)
        
        
        atk       = ALL_ATTACKS[attack_id]
        defender  = session.other(attacker)

        # ── 1) BEAM ───────────────────────────────
        if atk.type is AttackType.BEAM:
            if session.pending_beam:
                prev_player, prev_atk = session.pending_beam
                # now we have two beams in play:
                #   prev_player fired prev_atk, attacker just fired atk
                winner = random.choice([prev_player, attacker])
                loser  = session.other(winner)
                clash = random.randint(1,2)
                
                # test specific clashes
                #clash = 2
                
                webhooks = await ctx.channel.webhooks()
                webhook  = discord.utils.get(webhooks, name="Impersonator")
                if webhook is None:
                    webhook = await ctx.channel.create_webhook(name="Impersonator")
                loser.hp -= 25
                loser_member = loser.member
                winner_member = winner.member
                loser_atk = prev_atk if loser is prev_player else atk
                if clash == 1:
                    await ctx.send("https://tenor.com/view/dbz-dragon-ball-z-kakarot-goku-vegeta-gif-16782871")
                    await asyncio.sleep(0.5)
                    await webhook.send(
                        content=f"IT'S HOPELESS, {winner.name.upper()}! THERE'S NO WAY YOU CAN STOP MY {loser_atk.name.upper()}!",
                        username=loser_member.display_name,
                        avatar_url=loser_member.display_avatar.url,
                        wait = True
                    )

                    await asyncio.sleep(1.8)
                    await ctx.send("https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExNGVjNjl6NmdtMWVpdDBpMjkzeHM0NHZsOTFycHgxeDl5eTR1eWl2ciZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/TBI6xlcO7y1jM1fgx0/giphy.gif")
                    await asyncio.sleep(0.8)
                    await webhook.send(
                        content=f"GHHNNNNN. KAIOKEN...\n# **TIMES FOUR!!!**",
                        username=winner_member.display_name,
                        avatar_url=winner_member.display_avatar.url,
                        wait = True
                    )
                    await asyncio.sleep(2)
                    await webhook.send(
                        content=f"No!... They're beating me!...**GAHHHH**",
                        username=loser_member.display_name,
                        avatar_url=loser_member.display_avatar.url,
                        wait = True
                    )
                
                elif clash == 2:
                    await ctx.send("https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExdXVwcXZhNmlxYXRxYXllbzRrM21raXNsZnhnbXp4OTdibzEwbXkyZiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/5ZyHBwztbHSk6q8BPb/giphy.gif")
                    await asyncio.sleep(0.2)
                    await webhook.send(
                        content=f"**YOU AND THIS WHOLE PLANET ARE DONE FOR!**",
                        username=loser_member.display_name,
                        avatar_url=loser_member.display_avatar.url,
                        wait = True
                    )
                    await asyncio.sleep(2)
                    humans = [m for m in ctx.guild.members if not m.bot and m != ctx.author and m != loser_member]
                    father = random.choice(humans)
                    await webhook.send(
                        content=f"Show him, {winner_member.display_name}....Let them see our combined power!",
                        username=father.display_name,
                        avatar_url=father.display_avatar.url,
                        wait = True
                    )
                    
                    await asyncio.sleep(1)
                    await webhook.send(
                        content=f"**YOU'RE FINISHED!**",
                        username=loser_member.display_name,
                        avatar_url=loser_member.display_avatar.url,
                        wait = True
                    )
                    
                    await asyncio.sleep(1)
                    await ctx.send("https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExM2RodG9pZmR2czRrbWRvNGtkb29odDh4YjZiY2EwZGxzeTl0azU5cSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/PUAvVpxS4x0nWDVFvj/giphy.gif")
                    await webhook.send(
                        content=f"# **HAAAAAAAAAAA!!!!**",
                        username=winner_member.display_name,
                        avatar_url=winner_member.display_avatar.url,
                        wait = True
                    )
                    await asyncio.sleep(2)
                    
                    await ctx.send("https://i.ytimg.com/vi/lGU_lSpznUY/maxresdefault.jpg")
                    await webhook.send(
                        content=f"This...can't...be happening..!!!",
                        username=loser_member.display_name,
                        avatar_url=loser_member.display_avatar.url,
                        wait = True
                    )
                    
                await ctx.send(
                    f"🔹 **{prev_player.name}** launched a **{prev_atk.name}**! \n"
                    f"🔹 **{attacker.name}** launches **{atk.name}**!\n"
                    f"💥 **Beam clash!** **{winner.name}** wins the coin flip; "
                    f"{loser.name} loses 25 HP (now {loser.hp})."
                )

                session.pending_beam = None
                await webhook.delete()


            else:
                # first beam of the duel
                session.pending_beam = (attacker, atk)
                await ctx.send(
                    f"🔹 **{attacker.name}** fires **{atk.name}**! "
                    f"{defender.name}, roll to, hopefully, clash."
                )

        # ── 2) INSTANT KILL ────────────────────────
        elif atk.type is AttackType.INSTANT:
            # zero out defender’s HP
            defender.hp = 0
            # announce the insta-kill
            webhooks = await ctx.channel.webhooks()
            webhook  = discord.utils.get(webhooks, name="Impersonator")
            if webhook is None:
                webhook = await ctx.channel.create_webhook(name="Impersonator")
            
            attacker_player = attacker
            defender_player = session.other(attacker_player)

            author = attacker_player.member
            victim  = defender_player.member
            if atk.name == "Hakai":
                gify = random.randint(1,2)
                await webhook.send(
                    content=f"Sorry, {victim.display_name}, but your luck has run out.",
                    username=author.display_name,
                    avatar_url=author.display_avatar.url,
                    wait = True
                )
                await asyncio.sleep(1.7)
                await webhook.send(
                    content=f"# **Hakai.**",
                    username=author.display_name,
                    avatar_url=author.display_avatar.url,
                    wait = True
                )
                await asyncio.sleep(0.5)
                if gify == 1:
                    await ctx.send("https://cdn.discordapp.com/attachments/1380198124081119435/1381659253332512908/voce-usou-hankai.gif?ex=684851f3&is=68470073&hm=5757914c5e4a196c8e62f52ee35a3581c199a90c0336cb7caa6b4f379bdb47ee&")
                elif gify == 2:
                    await ctx.send("https://media.discordapp.net/attachments/1380198124081119435/1381659252946370730/goku-manga-hakai-hakai.gif?ex=684851f3&is=68470073&hm=59775cb6f7cfa58d9bf579a77c2cdedea4f295007c71721d80c826f75e176a2c&=&width=996&height=560")
            
            elif atk.name == "Soul Punisher":
                soulPunisher = random.randint(1,2)
                humans = [m for m in ctx.guild.members if not m.bot and m != ctx.author and m != victim]
                member1 = random.choice(humans)
                member2 = random.choice(humans)
                await webhook.send(
                    content=f"I am not *{member1.display_name}* or *{member2.display_name}*! I am **{author.display_name}**! It's over {victim.display_name}, I've come for you!",
                    username=author.display_name,
                    avatar_url=author.display_avatar.url,
                    wait = True
                )
                await asyncio.sleep(1.5)                
                await webhook.send(
                    content=f"Every force you create has an echo. Your own bad energy will be your undoing!",
                    username=author.display_name,
                    avatar_url=author.display_avatar.url,
                    wait = True
                )
                await asyncio.sleep(0.5)
                if soulPunisher == 1:
                    await ctx.send(f"https://i.makeagif.com/media/4-15-2022/1oo8uC.gif")
                elif soulPunisher == 2:
                    await ctx.send(f"https://i.pinimg.com/originals/f0/b4/77/f0b477f65deb1fca584efdb5542e665b.gif")
            
            await asyncio.sleep(0.7)
            self.record_win(attacker.member)
            await ctx.send(f"💀 **{attacker.name}** lands **{atk.name}**! Instant KO!")
            await ctx.send(
                f"🏆 **{attacker.name}** wins the duel! "
                f"(They now have {self.wins[str(attacker.member.id)]} total wins.)"
            )
            del self.sessions[ctx.channel.id]
            return
    
        # ── 3) BACKFIRE ────────────────────────
        elif atk.type is AttackType.BACKFIRE:
            # mark attacker dead
            attacker.hp = 0

            # grab Player objects
            attacker_player = attacker
            defender_player = session.other(attacker_player)

            # grab the underlying discord.Member
            author = attacker_player.member
            victim  = defender_player.member

            # get or create our “Impersonator” webhook
            webhooks = await ctx.channel.webhooks()
            webhook  = discord.utils.get(webhooks, name="Impersonator")
            if webhook is None:
                webhook = await ctx.channel.create_webhook(name="Impersonator")

            # 1) Impersonate the attacker freaking out
            await webhook.send(
                content="Wha—What the?!",
                username=author.display_name,
                avatar_url=author.display_avatar.url,
                wait = True
            )
            await asyncio.sleep(0.2)
            await webhook.send(
                content="https://i.makeagif.com/media/1-28-2019/P8wA11.gif",
                username=author.display_name,
                avatar_url=author.display_avatar.url,
                wait = True
            )

            # 2) Then have the victim taunt back
            await asyncio.sleep(1.5)
            await webhook.send(
                content=f"Now what was that supposed to be, {author.display_name}?",
                username=victim.display_name,
                avatar_url=victim.display_avatar.url,
                wait = True
            )
            await asyncio.sleep(0.9)
            await webhook.send(
                content="https://media.discordapp.net/attachments/1380188830753362063/1381724686966198423/broly-goku.gif",
                username=victim.display_name,
                avatar_url=victim.display_avatar.url,
                wait = True
            )
            await asyncio.sleep(1.5)
            await webhook.send(
                content="https://media.discordapp.net/attachments/1380188830753362063/1381724687528230972/broly-vs-goku-broly.gif",
                username=victim.display_name,
                avatar_url=victim.display_avatar.url,
                wait = True
            )

            # clean up
            await webhook.delete()

            # finally post the outcome as the bot itself
            await ctx.send(
                f"🔥 **{author.display_name}** tried to attack but it backfired! "
                f"{author.display_name} is KO’d!"
            )

        # ── 4) STRIKES & SPECIALS ──────────────────
        elif atk.type is AttackType.SPECIAL:
        # beam vs special override
            if session.pending_beam and attacker != session.pending_beam[0]:
                beam_user, beam_atk = session.pending_beam
                loser = session.other(beam_user)
                loser.hp -= 25

                webhooks = await ctx.channel.webhooks()
                webhook  = discord.utils.get(webhooks, name="Impersonator")
                if webhook is None:
                    webhook = await ctx.channel.create_webhook(name="Impersonator")
                attack_winner = beam_user.member
                attack_loser = loser.member
                
                if beam_atk.name == "Kamehameha":
                    await webhook.send(
                        content=f"KAAAAMEEEEE",
                        username=attack_winner.display_name,
                        avatar_url=attack_winner.display_avatar.url,
                        wait = True
                    )
                    await asyncio.sleep(0.9)
                    await webhook.send(
                        content=f"HAAAAMEEEEEE",
                        username=attack_winner.display_name,
                        avatar_url=attack_winner.display_avatar.url,
                        wait = True
                    )
                    
                    await asyncio.sleep(0.9)
                    await webhook.send(
                        content=f"# **HAAAAAAAAAAAAAA**",
                        username=attack_winner.display_name,
                        avatar_url=attack_winner.display_avatar.url,
                        wait = True
                    )
                    
                    await asyncio.sleep(0.5)
                    await ctx.send("https://i.pinimg.com/originals/31/37/89/3137899f774569326119b5992d3a4409.gif")
                    await asyncio.sleep(0.5)

                elif beam_atk.name == "Final Flash":
                    await webhook.send(
                        content=f"YOU COCKY BASTARD. ARE YOU BRAVE ENOUGH TO TAKE THIS ONE, {attack_loser.display_name.upper()}?!",
                        username=attack_winner.display_name,
                        avatar_url=attack_winner.display_avatar.url,
                        wait = True
                    )
                    await asyncio.sleep(1.2)
                    await webhook.send(
                        content=f"FINALLLLL",
                        username=attack_winner.display_name,
                        avatar_url=attack_winner.display_avatar.url,
                        wait = True
                    )
                    await asyncio.sleep(0.9)
                    await webhook.send(
                        content=f"# **FLASHHHHHHH**",
                        username=attack_winner.display_name,
                        avatar_url=attack_winner.display_avatar.url,
                        wait = True
                    )
                    await asyncio.sleep(0.5)
                    vegetGif = random.randint(1,2)
                    if vegetGif == 1:
                        await ctx.send("https://i.pinimg.com/originals/89/fb/05/89fb055e736889c54778fa9348c2f0e6.gif")
                    elif vegetGif == 2:
                        await ctx.send("https://cdn.discordapp.com/attachments/1380198124081119435/1381662696625143919/0a12d9726479da1c6b3ab9ac9e4d044c.gif?ex=68485528&is=684703a8&hm=a84ed39da231d0ae3556ee20e0642f8d1c7b4f64dfdd15afa07e3951d9ebc24b&")

                elif beam_atk.name == "Spirit Bomb":
                    spiritbomb = random.randint(1,3)
                    msg = await webhook.send(
                        content="Everyone! I need you all to lend me your energy!",
                        username=attack_winner.display_name,
                        avatar_url=attack_winner.display_avatar.url,
                        wait=True
                    )
                    gif = await webhook.send(
                        content="https://media.tenor.com/8Ltt65SLeFUAAAAM/genki-dama-spirit-bomb.gif",
                        username=attack_winner.display_name,
                        avatar_url=attack_winner.display_avatar.url,
                        wait=True
                    )
                    await asyncio.sleep(4)
                    await msg.edit(content=f"IT'S READY!")
                    await gif.edit(content="https://miro.medium.com/v2/resize:fit:884/1*ZTUASIVTMSDYY7K4ZSq98g.gif")
                    await asyncio.sleep(3)
                    await msg.edit(content=f"# **TAKE THIS!**")
                    await asyncio.sleep(0.5)
                    if spiritbomb == 1:
                        await gif.edit(content="https://media.discordapp.net/attachments/1380198124081119435/1381660256123224124/goku.gif?ex=684852e3&is=68470163&hm=b15c1caed68b90669825aa83a92071fce206fdc0f8924598fd4fa918063cec8e&=&width=1280&height=720")
                    elif spiritbomb == 2:
                        await gif.edit(content="https://media.discordapp.net/attachments/1380198124081119435/1381660256827998208/dragon-ball-z-one-piece.gif?ex=684852e3&is=68470163&hm=e1e1167e26a19f4a337e4f038eaa5abb915ef1fd7c39b61bcf8aa9bdc04c58fd&=&width=748&height=422")
                    elif spiritbomb == 3:
                        await gif.edit(content="https://media.discordapp.net/attachments/1380198124081119435/1381660257230786711/goku-genkidama.gif?ex=684852e3&is=68470163&hm=91f1531f694f51aee054aed5592a263f68604bef666930af08ad9bb0596ccba6&=&width=746&height=562")

                elif beam_atk.name == "Getsuga Tensho":
                    await webhook.send(
                        content="Getsuga....",
                        username=attack_winner.display_name,
                        avatar_url=attack_winner.display_avatar.url,
                        wait=True
                    )
                    await asyncio.sleep(0.9)
                    await webhook.send(
                        content="# **Tensho!**",
                        username=attack_winner.display_name,
                        avatar_url=attack_winner.display_avatar.url,
                        wait=True
                    )
                    await asyncio.sleep(0.5)
                    await ctx.send("https://cdn.discordapp.com/attachments/1380198124081119435/1381659616487804988/ichigo-kurosaki-ichigo.gif?ex=6848524a&is=684700ca&hm=41538f4748df2d9b2188b9adaace917476e11f8e1fdbd18a887e55e5178a2b6e&")

                elif beam_atk.name == "Hollow Purple":
                    await webhook.send(
                        content="Nine Ropes, Polarized Light, Crow and Declaration, Between Front and Back...",
                        username=attack_winner.display_name,
                        avatar_url=attack_winner.display_avatar.url,
                        wait=True
                    )
                    await asyncio.sleep(0.9)
                    await webhook.send(
                        content="## **Hollow Purple**",
                        username=attack_winner.display_name,
                        avatar_url=attack_winner.display_avatar.url,
                        wait=True
                    )
                    await asyncio.sleep(0.5)
                    await ctx.send(f"https://media.discordapp.net/attachments/1380198124081119435/1381663464073728130/gojo-gojo-satoru.gif?ex=684855df&is=6847045f&hm=3954f92f96123a0ceeb8fb4d24b8a57906aa925ea4738f469d59760a530a2d3d&=&width=996&height=456")

                elif beam_atk.name == "Galick Gun":
                    await webhook.send(
                        content=f"NOW, {attack_loser.display_name.upper()}, PREPARE YOURSELF FOR OBLIVION!",
                        username=attack_winner.display_name,
                        avatar_url=attack_winner.display_avatar.url,
                        wait=True
                    )
                    await asyncio.sleep(1)
                    await webhook.send(
                        content=f"# **GALICK GUN!!**",
                        username=attack_winner.display_name,
                        avatar_url=attack_winner.display_avatar.url,
                        wait=True
                    )
                    await asyncio.sleep(0.5)
                    await ctx.send("https://i.namu.wiki/i/179VyMsH9ROjqh5liRq20bJ3VXFFb0CyGPGmxtfFrR3T6IpclPJX1QiahVN1bS11myTwJMsoo8NLnFb9pOqRZQ.gif")

                
                # mention both moves by name
                await ctx.send(
                    f"🔹 **{beam_user.name}** launches **{beam_atk.name}**!\n"
                    f"✨ **{attacker.name}** attempts **{atk.name}**!\n"
                    f"💥 **{beam_user.name}**’s **{beam_atk.name}** overwhelms "
                    f"{attacker.name}’s **{atk.name}**! "
                    f"{loser.name} loses 25 HP (now {loser.hp})."
                )

                session.pending_beam = None
                await webhook.delete()


            else:
                # no beam pending, treat as normal special prompt
                session.pending_special = (attacker, atk)
                await ctx.send(
                    f"✨ **{attacker.name}** rolls **{atk.name}**!\n"
                    "Type `!stick` or `!s` to lock it in for 25 HP or `!reroll` to try again."
                )
                return
            
        # 5) STRIKE (fallback for non‐beam, non‐instant, non‐backfire, non‐special)
        elif atk.type is AttackType.STRIKE:
            # beam beats strike
            if session.pending_beam and attacker != session.pending_beam[0]:
                beam_user, beam_atk = session.pending_beam
                loser = session.other(beam_user)
                loser.hp -= 25

                webhooks = await ctx.channel.webhooks()
                webhook  = discord.utils.get(webhooks, name="Impersonator")
                if webhook is None:
                    webhook = await ctx.channel.create_webhook(name="Impersonator")
                attack_winner = beam_user.member
                attack_loser = loser.member
                
                if beam_atk.name == "Kamehameha":
                    await webhook.send(
                        content=f"KAAAAMEEEEE",
                        username=attack_winner.display_name,
                        avatar_url=attack_winner.display_avatar.url,
                        wait = True
                    )
                    await asyncio.sleep(0.9)
                    await webhook.send(
                        content=f"HAAAAMEEEEEE",
                        username=attack_winner.display_name,
                        avatar_url=attack_winner.display_avatar.url,
                        wait = True
                    )
                    
                    await asyncio.sleep(0.9)
                    await webhook.send(
                        content=f"# **HAAAAAAAAAAAAAA**",
                        username=attack_winner.display_name,
                        avatar_url=attack_winner.display_avatar.url,
                        wait = True
                    )
                    
                    await asyncio.sleep(0.5)
                    await ctx.send("https://i.pinimg.com/originals/31/37/89/3137899f774569326119b5992d3a4409.gif")
                    await asyncio.sleep(0.5)

                elif beam_atk.name == "Final Flash":
                    await webhook.send(
                        content=f"YOU COCKY BASTARD. ARE YOU BRAVE ENOUGH TO TAKE THIS ONE, {attack_loser.display_name.upper()}?!",
                        username=attack_winner.display_name,
                        avatar_url=attack_winner.display_avatar.url,
                        wait = True
                    )
                    await asyncio.sleep(1.2)
                    await webhook.send(
                        content=f"FINALLLLL",
                        username=attack_winner.display_name,
                        avatar_url=attack_winner.display_avatar.url,
                        wait = True
                    )
                    await asyncio.sleep(0.9)
                    await webhook.send(
                        content=f"# **FLASHHHHHHH**",
                        username=attack_winner.display_name,
                        avatar_url=attack_winner.display_avatar.url,
                        wait = True
                    )
                    await asyncio.sleep(0.5)
                    vegetGif = random.randint(1,2)
                    if vegetGif == 1:
                        await ctx.send("https://i.pinimg.com/originals/89/fb/05/89fb055e736889c54778fa9348c2f0e6.gif")
                    elif vegetGif == 2:
                        await ctx.send("https://cdn.discordapp.com/attachments/1380198124081119435/1381662696625143919/0a12d9726479da1c6b3ab9ac9e4d044c.gif?ex=68485528&is=684703a8&hm=a84ed39da231d0ae3556ee20e0642f8d1c7b4f64dfdd15afa07e3951d9ebc24b&")

                elif beam_atk.name == "Spirit Bomb":
                    spiritbomb = random.randint(1,3)
                    msg = await webhook.send(
                        content="Everyone! I need you all to lend me your energy!",
                        username=attack_winner.display_name,
                        avatar_url=attack_winner.display_avatar.url,
                        wait=True
                    )
                    gif = await webhook.send(
                        content="https://media.tenor.com/8Ltt65SLeFUAAAAM/genki-dama-spirit-bomb.gif",
                        username=attack_winner.display_name,
                        avatar_url=attack_winner.display_avatar.url,
                        wait=True
                    )
                    await asyncio.sleep(4)
                    await msg.edit(content=f"IT'S READY!")
                    await gif.edit(content="https://miro.medium.com/v2/resize:fit:884/1*ZTUASIVTMSDYY7K4ZSq98g.gif")
                    await asyncio.sleep(3)
                    await msg.edit(content=f"# **TAKE THIS!**")
                    await asyncio.sleep(0.5)
                    if spiritbomb == 1:
                        await gif.edit(content="https://media.discordapp.net/attachments/1380198124081119435/1381660256123224124/goku.gif?ex=684852e3&is=68470163&hm=b15c1caed68b90669825aa83a92071fce206fdc0f8924598fd4fa918063cec8e&=&width=1280&height=720")
                    elif spiritbomb == 2:
                        await gif.edit(content="https://media.discordapp.net/attachments/1380198124081119435/1381660256827998208/dragon-ball-z-one-piece.gif?ex=684852e3&is=68470163&hm=e1e1167e26a19f4a337e4f038eaa5abb915ef1fd7c39b61bcf8aa9bdc04c58fd&=&width=748&height=422")
                    elif spiritbomb == 3:
                        await gif.edit(content="https://media.discordapp.net/attachments/1380198124081119435/1381660257230786711/goku-genkidama.gif?ex=684852e3&is=68470163&hm=91f1531f694f51aee054aed5592a263f68604bef666930af08ad9bb0596ccba6&=&width=746&height=562")

                elif beam_atk.name == "Getsuga Tensho":
                    await webhook.send(
                        content="Getsuga....",
                        username=attack_winner.display_name,
                        avatar_url=attack_winner.display_avatar.url,
                        wait=True
                    )
                    await asyncio.sleep(0.9)
                    await webhook.send(
                        content="# **Tensho!**",
                        username=attack_winner.display_name,
                        avatar_url=attack_winner.display_avatar.url,
                        wait=True
                    )
                    await asyncio.sleep(0.5)
                    await ctx.send("https://cdn.discordapp.com/attachments/1380198124081119435/1381659616487804988/ichigo-kurosaki-ichigo.gif?ex=6848524a&is=684700ca&hm=41538f4748df2d9b2188b9adaace917476e11f8e1fdbd18a887e55e5178a2b6e&")

                elif beam_atk.name == "Hollow Purple":
                    await webhook.send(
                        content="Nine Ropes, Polarized Light, Crow and Declaration, Between Front and Back...",
                        username=attack_winner.display_name,
                        avatar_url=attack_winner.display_avatar.url,
                        wait=True
                    )
                    await asyncio.sleep(0.9)
                    await webhook.send(
                        content="## **Hollow Purple**",
                        username=attack_winner.display_name,
                        avatar_url=attack_winner.display_avatar.url,
                        wait=True
                    )
                    await asyncio.sleep(0.5)
                    await ctx.send(f"https://media.discordapp.net/attachments/1380198124081119435/1381663464073728130/gojo-gojo-satoru.gif?ex=684855df&is=6847045f&hm=3954f92f96123a0ceeb8fb4d24b8a57906aa925ea4738f469d59760a530a2d3d&=&width=996&height=456")

                elif beam_atk.name == "Galick Gun":
                    await webhook.send(
                        content=f"NOW, {attack_loser.display_name.upper()}, PREPARE YOURSELF FOR OBLIVION!",
                        username=attack_winner.display_name,
                        avatar_url=attack_winner.display_avatar.url,
                        wait=True
                    )
                    await asyncio.sleep(0.9)
                    await webhook.send(
                        content=f"# **GALICK GUN!!**",
                        username=attack_winner.display_name,
                        avatar_url=attack_winner.display_avatar.url,
                        wait=True
                    )
                    await asyncio.sleep(0.5)
                    await ctx.send("https://i.namu.wiki/i/179VyMsH9ROjqh5liRq20bJ3VXFFb0CyGPGmxtfFrR3T6IpclPJX1QiahVN1bS11myTwJMsoo8NLnFb9pOqRZQ.gif")
                    
                await ctx.send(
                    f"🔹 **{beam_user.name}** launches **{beam_atk.name}**!\n"
                    f"🔸 **{attacker.name}** attempts **{atk.name}**!\n"
                    f"💥 **{beam_user.name}**’s **{beam_atk.name}** overwhelms "
                    f"{attacker.name}’s **{atk.name}**! "
                    f"{loser.name} loses 25 HP (now {loser.hp})."
                )

                session.pending_beam = None
                await webhook.delete()
                
            else:
                # normal strike
                defender.hp -= 25
                attacker_player = attacker
                defender_player = session.other(attacker_player)

                # grab the underlying discord.Member
                author = attacker_player.member
                victim  = defender_player.member
                if (atk.name == "Invincible Beatdown"):
                    titlecard = random.randint(1,2)
                    webhooks = await ctx.channel.webhooks()
                    webhook = discord.utils.get(webhooks, name="Impersonator")
                    if webhook is None:
                        webhook = await ctx.channel.create_webhook(name="Impersonator")
                        
                    await webhook.send(
                        content=f"Is this what you wanted, {victim.display_name}?",
                        username=author.display_name,
                        avatar_url=author.display_avatar.url,
                        wait = True
                    )
                    await asyncio.sleep(1)
                    await webhook.send(
                        content=f"You enjoy yourself?",
                        username=author.display_name,
                        avatar_url=author.display_avatar.url,
                        wait = True
                    )
                    await asyncio.sleep(1.5)
                    await webhook.send(
                        content=f"STILL HAVING FUN?",
                        username=author.display_name,
                        avatar_url=author.display_avatar.url,
                        wait = True
                    )
                    await asyncio.sleep(1.3)
                    await webhook.send(
                        content=f"**ANSWER ME!**",
                        username=author.display_name,
                        avatar_url=author.display_avatar.url,
                        wait = True
                    )
                    await asyncio.sleep(1.2)
                    await webhook.send(
                        content="I take the good with the bad.",
                        username=victim.display_name,
                        avatar_url=victim.display_avatar.url,
                        wait = True
                    )
                    
                    await asyncio.sleep(1.5)
                    await webhook.send(
                        content=f"# **GRAAAAAAHHHHHH**",
                        username=author.display_name,
                        avatar_url=author.display_avatar.url,
                        wait = True
                    )
                    await asyncio.sleep(0.5)
                    await webhook.delete()
                    if titlecard == 1:
                        await ctx.send("https://media.discordapp.net/attachments/1380198124081119435/1381656268032315533/invincible-punch-invincible.gif?ex=68484f2c&is=6846fdac&hm=7ffef3dccbe7001154d01007ad17cf29b1f245770091690f8c2e119a5c1be711&=&width=996&height=562")
                    elif titlecard == 2:
                        await ctx.send("https://preview.redd.it/characters-using-their-head-btw-congrats-to-the-sub-for-100k-v0-fvupe2avvgoe1.gif?width=640&crop=smart&auto=webp&s=0d80ce208df2ed15738d51a91211ac9e71b61894")
                
                elif (atk.name == "Black Flash"):
                    blackflash = random.randint(1,6)
                    await webhook.send(
                        content=f"The sparks of black do not choose who to bless, {victim.display_name}.",
                        username=author.display_name,
                        avatar_url=author.display_avatar.url,
                        wait = True
                    )
                    await asyncio.sleep(1.2)
                    await webhook.send(
                        content=f"# **Black Flash**",
                        username=author.display_name,
                        avatar_url=author.display_avatar.url,
                        wait = True
                    )
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
                
                elif (atk.name == "Serious Series"):
                    series = random.randint(1,2)
                    await webhook.send(
                        content=f"Serious series...",
                        username=author.display_name,
                        avatar_url=author.display_avatar.url,
                        wait = True
                    )
                    await asyncio.sleep(1.2)
                    if series == 1:
                        await webhook.send(
                            content=f"# **Serious Punch**",
                            username=author.display_name,
                            avatar_url=author.display_avatar.url,
                            wait = True
                        )
                        await asyncio.sleep(0.5)
                        await ctx.send(f"https://media.discordapp.net/attachments/1380198124081119435/1381660383927992390/saitama-serious-vs.gif?ex=68485301&is=68470181&hm=5e56c4f90ffffc4a182aabae9c39fb123250654d031ada0d3dc0c5f238bf8b8a&=&width=996&height=562")
                    elif series == 2:
                        await webhook.send(
                            content=f"# **Serious Tableflip**",
                            username=author.display_name,
                            avatar_url=author.display_avatar.url,
                            wait = True
                        )
                        await asyncio.sleep(0.5)
                        await ctx.send(f"https://media.discordapp.net/attachments/1380198124081119435/1381660383462428863/saitama-serious-vs-cosmic-garou-serious-series.gif?ex=68485301&is=68470181&hm=c73130b3f9b7616ca568774fa489c15e88b893fb9d6874c6dffcad27fda6ce54&=&width=748&height=422")
                
                elif (atk.name == "Rasengan"):
                    await webhook.send(
                            content=f"# **Rasengan!**",
                            username=author.display_name,
                            avatar_url=author.display_avatar.url,
                            wait = True
                        )
                    await asyncio.sleep(0.5)
                    await ctx.send("https://media.discordapp.net/attachments/1380198124081119435/1381658129766289539/minato.gif?ex=684850e8&is=6846ff68&hm=c29b72691cfe8e4914d105998b3dd1da8f22b80cbe5d14608949c15eadf5d0c0&=&width=996&height=592")
                
                await ctx.send(
                    f"🔸 **{attacker.name}** uses **{atk.name}**! "
                    f"{defender.name} loses 25 HP (now {defender.hp})."
                )

        # ── 5) End‐of‐turn housekeeping ─────────────
        # check for KO
        if session.is_over():
            winner = session.winner()
            self.record_win(winner.member)
            await ctx.send(
                f"🏆 **{winner.name}** wins the duel! "
                f"(They now have {self.wins[str(winner.member.id)]} total wins.)"
            )   
            del self.sessions[ctx.channel.id]
            return

        # swap turns
        session.turn = defender
        await ctx.send(f"🔄 Next: **{session.turn.name}** – type `!roll` or `!r`!")

    @commands.command(name="stick", aliases=["s"], help="Lock in your special for 25 HP")
    async def stick(self, ctx):
        session = self.sessions.get(ctx.channel.id)
        if not session or not session.in_progress:
            return await ctx.send("❓ There's no active fight? You tryna start one, fucker?")
        if not session.pending_special:
            return await ctx.send("❓ You have no special to lock in, dumbfuck.")
        
        attacker, atk = session.pending_special
        if ctx.author != attacker.member:
            return await ctx.send("🚫 That’s not your special to stick, you moron!")

        defender = session.other(attacker)
        defender.hp -= 25
        
        webhooks = await ctx.channel.webhooks()
        webhook  = discord.utils.get(webhooks, name="Impersonator")
        if webhook is None:
            webhook = await ctx.channel.create_webhook(name="Impersonator")
        attackie = attacker.member
        
        if atk.name == "I Am Atomic":
            await webhook.send(
                content=f"I am...",
                username=attackie.display_name,
                avatar_url=attackie.display_avatar.url,
                wait = True
            )
            await asyncio.sleep(1)
            await webhook.send(
                content=f"## **Atomic.**",
                username=attackie.display_name,
                avatar_url=attackie.display_avatar.url,
                wait = True
            )
            await ctx.send(f"https://cdn.discordapp.com/attachments/1380198124081119435/1381662788023226418/forcegate1.gif?ex=6848553e&is=684703be&hm=b2a2ebbbcfdbab30d91edb9a4b47df8f2fd588f1508d34142db3844b1a08d816&")

        elif atk.name == "Domain Expansion":
            domain = random.randint(1,4)
            await webhook.send(
                content=f"Domain Expansion...",
                username=attackie.display_name,
                avatar_url=attackie.display_avatar.url,
                wait = True
            )
            await asyncio.sleep(0.8)
            if domain == 1:
                await webhook.send(
                    content=f"# **Infinite Void**",
                    username=attackie.display_name,
                    avatar_url=attackie.display_avatar.url,
                    wait = True
                )
                await asyncio.sleep(0.5)
                await ctx.send(f"https://cdn.discordapp.com/attachments/1380198124081119435/1381663168165838858/domain-expansion.gif?ex=68485599&is=68470419&hm=9a5b28490f449f395d46fc988a1f1ba5d8d20e642d620e31848bce28e8ef3689&")
            elif domain == 2:
                await webhook.send(
                    content=f"# **Malevolent Shrine**",
                    username=attackie.display_name,
                    avatar_url=attackie.display_avatar.url,
                    wait = True
                )
                await asyncio.sleep(0.5)
                await ctx.send(f"https://media.discordapp.net/attachments/1380198124081119435/1381663168560107550/sukuna-mahoraga.gif?ex=68485599&is=68470419&hm=6d0e4649efaaf6a783d319132af132d27206989f53c127e53042b455f04ab2d2&=&width=996&height=446")
            elif domain == 3:
                await webhook.send(
                    content=f"# **Self Embodiment of Perfection**",
                    username=attackie.display_name,
                    avatar_url=attackie.display_avatar.url,
                    wait = True
                )
                await asyncio.sleep(0.5)
                await ctx.send(f"https://media.discordapp.net/attachments/1380198124081119435/1381663169042186240/jjk-jujutsu-kaisen.gif?ex=68485599&is=68470419&hm=1214cafadc08226374d5ebfe470a36ec9e936285ab7d3738260ac3fe1b748bff&=&width=996&height=562")
            elif domain == 4:
                await webhook.send(
                    content=f"# **Chimera Shadow Garden**",
                    username=attackie.display_name,
                    avatar_url=attackie.display_avatar.url,
                    wait = True
                )
                await asyncio.sleep(0.5)
                await ctx.send(f"https://media.discordapp.net/attachments/1380198124081119435/1381663169423999136/megumi-fushiguro-megumi-domain-expansion.gif?ex=68485599&is=68470419&hm=b5cec5b9949ecf3eb1d42e8a855740c6fb81ba53a5a7cc48089fb5bba271efe0&=&width=996&height=562")

        elif atk.name == "Bat Whack":
            await ctx.send(f"https://tenor.com/view/the-shusher-bat-staff-rod-gif-8855179341029231927")
            await asyncio.sleep(0.2)
            await ctx.send("https://youtu.be/f8mL0_4GeV0?si=r5U5AsQ74Mv4M5ZK")
        
        await ctx.send(
            f"✨ **{attacker.name}** locks in **{atk.name}**! "
            f"{defender.name} loses 25 HP (now {defender.hp})."
        )

        session.pending_special = None
        await webhook.delete()


        if session.is_over():
            winner = session.winner()
            self.record_win(winner.member)
            await ctx.send(
                f"🏆 **{winner.name}** wins the duel! "
                f"(They now have {self.wins[str(winner.member.id)]} total wins.)"
            )
            del self.sessions[ctx.channel.id]
            return

        session.turn = defender
        await ctx.send(f"🔄 Next: **{session.turn.name}** – type `!roll` or `!r`!")

    @commands.command(name="reroll", help="Roll again for a different attack")
    async def reroll(self, ctx):
        session = self.sessions.get(ctx.channel.id)
        if not session or not session.in_progress:
            return await ctx.send("❓ No fight here.")
        if not session.pending_special:
            return await ctx.send("❓ You have no special to reroll.")
        
        attacker, _ = session.pending_special
        if ctx.author != attacker.member:
            return await ctx.send("🚫 That’s not your reroll to use!")

        session.pending_special = None
        await ctx.send(f"🔄 **{attacker.name}** rerolls their special!")
        # re-invoke roll logic for you
        await self.roll(ctx)

    @commands.command(name="end", help="End the fight in a draw")
    async def end(self, ctx):
        session = self.sessions.get(ctx.channel.id)
        if not session or not session.in_progress:
            return await ctx.send("❓ No fight to end here.")
        if ctx.author not in (session.fucker.member, session.fucked.member):
            return await ctx.send("🚫 You’re not in this fight!")
        await ctx.send(f"{ctx.author.display_name} ended the fight early. What a bitch.")
        del self.sessions[ctx.channel.id]
        
    @commands.command(name="leaderboard", aliases=["lb"])
    async def leaderboard(self, ctx):
        """Show top win-counts."""
        if not self.wins:
            return await ctx.send("No victories have been recorded yet.")

        # build a list of (member_id, wins) sorted descending
        sorted_wins = sorted(
            self.wins.items(),
            key=lambda kv: kv[1],
            reverse=True
        )

        # build an embed
        embed = discord.Embed(
            title="🏆 Battle Leaderboard",
            color=discord.Color.gold()
        )
        description = ""
        for i, (uid, count) in enumerate(sorted_wins[:10], start=1):
            member = ctx.guild.get_member(int(uid))
            name = member.display_name if member else f"<@{uid}>"
            description += f"**{i}.** {name} — {count} wins\n"
        embed.description = description

        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    print("Loaded")
    await bot.add_cog(Battle(bot))

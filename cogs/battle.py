# battle.py
import random
import discord
from discord.ext import commands
import asyncio

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
                f"**{self.session.turn.name}** goes first—use `!roll`!"
            ),
            view=None
        )

    @discord.ui.button(label="Deny", style=discord.ButtonStyle.danger)
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.session.fucked.member:
            return await interaction.response.send_message("You can’t deny this!", ephemeral=True)
        insults = ["You a bitch fr.", "Coward.", "Pathetic.", "Filthy monkey...can't even fight back.", "Are you trembling?", "Too much of a power gap, huh?", "What's wrong? Feeling chickenshit?", "Oh. Well, since they declined & i have your attention, did you know that The FitnessGram Pacer Test is a multistage aerobic capacity test that progressively gets more difficult as it continues. The 20 meter pacer test will begin in 30 seconds. Line up at the start. The running speed starts slowly but gets faster each minute after you hear this signal bodeboop. A sing lap should be completed every time you hear this sound. ding. Remember to run in a straight line and run as long as possible. The second time you fail to complete a lap before the sound, your test is over. The test will begin on the word start. On your mark. Get ready!… Start! ding"]
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

    @commands.command(name="challenge", help="Invite someone to a 1v1 fight")
    async def challenge(self, ctx, opponent: discord.Member):
        if ctx.channel.id in self.sessions:
            return await ctx.send("🚫 A battle is already in progress!")
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

    @commands.command(name="roll", help="Roll your attack")
    async def roll(self, ctx):
        session = self.sessions.get(ctx.channel.id)
        if not session or not session.in_progress:
            return await ctx.send("❓ No active fight to roll in.")
        attacker = session.turn
        if ctx.author != attacker.member:
            return await ctx.send(f"⌛ Not your turn—it's {attacker.name}'s.")
        
        # **Prevent a new roll if you must stick/reroll a pending special**
        if session.pending_special:
            return await ctx.send(
                f"🌀 You rolled a special earlier! "
                "Type `!stick` to lock it in or `!reroll` to roll again."
            )

        # 1) pick your attack
        attack_id = random.randint(1, 15)
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
                loser.hp -= 25

                await ctx.send(
                    f"🔹 **{prev_player.name}** launched a **{prev_atk.name}**! \n"
                    f"🔹 **{attacker.name}** launches **{atk.name}**!\n"
                    f"💥 **Beam clash!** **{winner.name}** wins the coin flip; "
                    f"{loser.name} loses 25 HP (now {loser.hp})."
                )

                session.pending_beam = None

            else:
                # first beam of the duel
                session.pending_beam = (attacker, atk)
                await ctx.send(
                    f"🔹 **{attacker.name}** fires **{atk.name}** beam! "
                    f"{defender.name}, roll to, hopefully, clash."
                )

        # ── 2) INSTANT KILL ────────────────────────
        elif atk.type is AttackType.INSTANT:
            # zero out defender’s HP
            defender.hp = 0
            # announce the insta-kill
            await ctx.send(f"💀 **{attacker.name}** lands **{atk.name}**! Instant KO!")
            # (optional) send a matching GIF
            # await asyncio.sleep(0.3)
            # await ctx.send("https://…your-instant-kill.gif…")
            # now end the duel
            await ctx.send(f"🏆 **{attacker.name}** wins the duel!")
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
                avatar_url=author.display_avatar.url
            )
            await asyncio.sleep(0.2)
            await webhook.send(
                content="https://i.makeagif.com/media/1-28-2019/P8wA11.gif",
                username=author.display_name,
                avatar_url=author.display_avatar.url
            )

            # 2) Then have the victim taunt back
            await asyncio.sleep(1.5)
            await webhook.send(
                content=f"Now what was that supposed to be, {author.display_name}?",
                username=victim.display_name,
                avatar_url=victim.display_avatar.url
            )
            await asyncio.sleep(0.9)
            await webhook.send(
                content="https://media.discordapp.net/attachments/1380188830753362063/1381724686966198423/broly-goku.gif",
                username=victim.display_name,
                avatar_url=victim.display_avatar.url
            )
            await asyncio.sleep(1.5)
            await webhook.send(
                content="https://media.discordapp.net/attachments/1380188830753362063/1381724687528230972/broly-vs-goku-broly.gif",
                username=victim.display_name,
                avatar_url=victim.display_avatar.url
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

                # mention both moves by name
                await ctx.send(
                    f"🔹 **{beam_user.name}** launches **{beam_atk.name}** beam!\n"
                    f"✨ **{attacker.name}** attempts **{atk.name}** special!\n"
                    f"💥 **{beam_user.name}**’s **{beam_atk.name}** overwhelms "
                    f"{attacker.name}’s **{atk.name}**! "
                    f"{loser.name} loses 25 HP (now {loser.hp})."
                )

                session.pending_beam = None

            else:
                # no beam pending, treat as normal special prompt
                session.pending_special = (attacker, atk)
                await ctx.send(
                    f"✨ **{attacker.name}** rolls **{atk.name}** special!\n"
                    "Type `!stick` to lock it in for 25 HP or `!reroll` to try again."
                )
                return

        # 5) STRIKE (fallback for non‐beam, non‐instant, non‐backfire, non‐special)
        elif atk.type is AttackType.STRIKE:
            # beam beats strike
            if session.pending_beam and attacker != session.pending_beam[0]:
                beam_user, beam_atk = session.pending_beam
                loser = session.other(beam_user)
                loser.hp -= 25

                await ctx.send(
                    f"🔹 **{beam_user.name}** launches **{beam_atk.name}** beam!\n"
                    f"🔸 **{attacker.name}** attempts **{atk.name}** strike!\n"
                    f"💥 **{beam_user.name}**’s **{beam_atk.name}** overwhelms "
                    f"{attacker.name}’s **{atk.name}**! "
                    f"{loser.name} loses 25 HP (now {loser.hp})."
                )

                session.pending_beam = None

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
                    await ctx.send(f"Is this what you wanted, {victim.display_name}?")
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
                        username=author.display_name,
                        avatar_url=author.display_avatar.url
                    )
                    await webhook.delete()
                    
                    await asyncio.sleep(1.5)
                    await ctx.send("# **GRAAAAAAHHHHHH**")
                    await asyncio.sleep(0.5)
                    if titlecard == 1:
                        await ctx.send("https://media.discordapp.net/attachments/1380198124081119435/1381656268032315533/invincible-punch-invincible.gif?ex=68484f2c&is=6846fdac&hm=7ffef3dccbe7001154d01007ad17cf29b1f245770091690f8c2e119a5c1be711&=&width=996&height=562")
                    elif titlecard == 2:
                        await ctx.send("https://preview.redd.it/characters-using-their-head-btw-congrats-to-the-sub-for-100k-v0-fvupe2avvgoe1.gif?width=640&crop=smart&auto=webp&s=0d80ce208df2ed15738d51a91211ac9e71b61894")
                
                elif (atk.name == "Black Flash"):
                    blackflash = random.randint(1,6)
                    await ctx.send(f"The sparks of black do not choose who to bless, {victim.display_name}.")
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
                
                elif (atk.name == "Serious Series"):
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
                
                elif (atk.name == "Rasengan"):
                    await ctx.send(f"# **Rasengan!**")
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
            await ctx.send(f"🏆 **{winner.name}** wins the duel!")
            del self.sessions[ctx.channel.id]
            return

        # swap turns
        session.turn = defender
        await ctx.send(f"🔄 Next: **{session.turn.name}** – type `!roll` or `!end`.")

    @commands.command(name="stick", help="Lock in your special for 25 HP")
    async def stick(self, ctx):
        session = self.sessions.get(ctx.channel.id)
        if not session or not session.in_progress:
            return await ctx.send("❓ No fight here.")
        if not session.pending_special:
            return await ctx.send("❓ You have no special to lock in.")
        
        attacker, atk = session.pending_special
        if ctx.author != attacker.member:
            return await ctx.send("🚫 That’s not your special to stick!")

        defender = session.other(attacker)
        defender.hp -= 25
        await ctx.send(
            f"✨ **{attacker.name}** locks in **{atk.name}**! "
            f"{defender.name} loses 25 HP (now {defender.hp})."
        )

        session.pending_special = None

        if session.is_over():
            winner = session.winner()
            await ctx.send(f"🏆 **{winner.name}** wins the duel!")
            del self.sessions[ctx.channel.id]
            return

        session.turn = defender
        await ctx.send(f"🔄 Next: **{session.turn.name}** – type `!roll` or `!end`.")

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
        await ctx.send("🤝 The fight ends in a draw.")
        del self.sessions[ctx.channel.id]

async def setup(bot: commands.Bot):
    print("Loaded")
    await bot.add_cog(Battle(bot))

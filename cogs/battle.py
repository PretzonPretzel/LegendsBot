import os
import random
from discord.ext import commands
from discord import Embed
import discord


class Player:
    def __init__(self, user):
        self.user = user
        self.hp = 100
    
    def take_damage(self, damage):
        self.hp -= damage
        
class PVPBattle:
    def __init__(self):
        self.players = {}
        

class Battle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    

async def setup(bot):
    await bot.add_cog(Battle(bot))
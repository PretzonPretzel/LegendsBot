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
        
    def add_player(self, player):
        self.players[player.user.id] = player
    
    def get_player(self, user):
        return self.players.get(user.id)
    
    def attack(self, attacker, target):
        damage = 25
        target.take_damage(damage)
        
        if target.health <= 0:
            return f'{target.user.name} died!'
        else:
            return f'{attacker.user.name} attacked {target.user.name}! Health remaining: {target.health}'

game = PVPBattle()


class Battle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    

async def setup(bot):
    await bot.add_cog(Battle(bot))
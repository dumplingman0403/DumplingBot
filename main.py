#!/usr/bin/env python3
# For asynchronous facilities.
from ast import alias
import asyncio

# For loading .env file
import os
from unicodedata import name
from dotenv import load_dotenv
# Discord API
import discord
from discord.ext import commands
# Import function
from modules.music.music_cog import Music
from modules.greeting_cog import Greetings
from modules.help.help_command import HelpCommand
from modules.manager import Manager

intents = discord.Intents.default()
intents.members = True
intents.messages = True

bot = commands.Bot(command_prefix='!', intents = intents)
bot.help_command = HelpCommand()
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')


# Add Music functions
bot.add_cog(Music(bot))
# Add Greeting Cog
bot.add_cog(Greetings(bot))
# Add utilities
bot.add_cog(Manager(bot))
load_dotenv()
# TOKEN = os.getenv("TOKEN")
# Heroku Config Var
TOKEN = os.environ.get("TOKEN")
bot.run(TOKEN)
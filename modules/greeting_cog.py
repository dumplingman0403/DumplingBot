import asyncio
import discord
from discord.ext import commands 
from modules.help.help_command import HelpCommand

class Greetings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None
        self.__original_help_command = bot.help_command
        # bot.help_command = HelpCommand()
        # bot.help_command.cog = self

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild
        if guild.system_channel is not None:
            to_send = f'Welcome {member.mention} to {guild.name}!'
            await guild.system_channel.send(to_send)
        await member.create_dm()
        await member.dm_channel.send(
            f'Hi {member.name}, welcome to {guild.name} server!'
        )

    @commands.command(name="hi", help="Say hi to user.")
    async def hello(self, ctx):
        member = ctx.author
        if self._last_member is None or self._last_member.id != member.id:
            await ctx.send('Hello {0.name}~'.format(member))
        else:
            await ctx.send('Hello {0.name}... This feels familiar.'.format(member))
        self._last_member = member
    
    # def cog_unload(self):
    #     self.bot.help_command = self.__original_help_command
    

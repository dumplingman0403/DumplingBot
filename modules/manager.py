import asyncio
import discord
from discord.ext import commands




class Manager(commands.Cog):
    
    def __init__(self, bot):
        
        self.bot = bot
    
    @commands.has_permissions(manage_messages=True)
    @commands.command(help="Delete number of messages. (need permission to manage messages)")
    async def delete(self, ctx, amount: int):
        """Delete number of messages"""
        await ctx.channel.purge(limit=amount)


    # @commands.has_permissions(administrator=True)
    # @commands.command()
    # async def create_role(self, ctx, *, member):
    #     await member.create_role() 
    #     pass
        
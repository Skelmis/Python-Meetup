import discord
from discord.ext import commands

from utils.util import GetMessage


class Echo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} cog has been loaded\n-----")

    @commands.command(
        name="echo", description="Repeats input back to you",
    )
    async def echo(self, ctx):
        message = await GetMessage(
            self.bot, ctx, "What do you want me to say?", "I will repeat your input."
        )
        if message:
            await ctx.message.delete()
            await ctx.send(message)


def setup(bot):
    bot.add_cog(Echo(bot))

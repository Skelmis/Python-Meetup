import platform
from pathlib import Path

import discord
from discord.ext import commands

from utils.jsonLoader import read_json

# Get current working directory
cwd = Path(__file__).parents[0]
cwd = str(cwd)
print(f"{cwd}\n-----")

# Defining a few things
secret_file = read_json("secrets")
bot = commands.Bot(command_prefix="-", case_insensitive=True)
bot.config_token = secret_file["token"]


@bot.event
async def on_ready():
    print(
        f"-----\nLogged in as: {bot.user.name} : {bot.user.id}\n-----\nMy current prefix is: -\n-----"
    )
    await bot.change_presence(
        activity=discord.Game(
            name=f"Hi, my names {bot.user.name}.\nUse - to interact with me!"
        )
    )  # This changes the bots 'activity'


@bot.event
async def on_command_error(ctx, error):
    # Ignore these errors
    ignored = (commands.CommandNotFound, commands.UserInputError)
    if isinstance(error, ignored):
        return

    raise error


@bot.command(name="hi", aliases=["hello"])
async def _hi(ctx):
    """
    A simple command which says hi to the author.
    """
    await ctx.send(f"Hi {ctx.author.mention}!")


@bot.command()
async def stats(ctx):
    """
    A useful command that displays bot statistics.
    """
    pythonVersion = platform.python_version()
    dpyVersion = discord.__version__
    serverCount = len(bot.guilds)
    memberCount = len(set(bot.get_all_members()))

    embed = discord.Embed(
        title=f"{bot.user.name} Stats",
        description="\uFEFF",
        colour=ctx.author.colour,
        timestamp=ctx.message.created_at,
    )

    embed.add_field(name="Bot Version:", value="0.0.1")
    embed.add_field(name="Python Version:", value=pythonVersion)
    embed.add_field(name="Discord.Py Version", value=dpyVersion)
    embed.add_field(name="Total Guilds:", value=serverCount)
    embed.add_field(name="Total Users:", value=memberCount)
    embed.add_field(name="Bot Developers:", value="<@271612318947868673>")

    embed.set_footer(text=f"Carpe Noctem | {bot.user.name}")
    embed.set_author(name=bot.user.name, icon_url=bot.user.avatar_url)

    await ctx.send(embed=embed)


@bot.command(aliases=["disconnect", "close", "stopbot"])
@commands.is_owner()
async def logout(ctx):
    """
    If the user running the command owns the bot then this will disconnect the bot from discord.
    """
    await ctx.send(f"Hey {ctx.author.mention}, I am now logging out :wave:")
    await bot.logout()


@bot.command()
async def echo(ctx, *, message=None):
    """
    A simple command that repeats the users input back to them.
    """
    message = message or "Please provide the message to be repeated."
    await ctx.message.delete()
    await ctx.send(message)


bot.run(bot.config_token)  # Runs our bot

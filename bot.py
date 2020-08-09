import re
import sys
import traceback

import discord
import motor.motor_asyncio
from discord.ext import commands

from utils.mongo import Document
from utils.util import SendEmbed
from utils.jsonLoader import read_json


DEFAULTPREFIX = "!"
secret_file = read_json("secrets")

# Use regex to parse mentions, much better than only supporting
# nickname mentions (<@!1234>)
# This basically ONLY matches a string that only consists of a mention
mention = re.compile(r"^<@!?(?P<id>\d+)>$")


async def get_prefix(bot, message):
    try:
        data = await bot.config.find(message.guild.id)
        # Make sure we have a useable prefix
        if not data or "prefix" not in data:
            return commands.when_mentioned_or(bot.DEFAULTPREFIX)(bot, message)
        return commands.when_mentioned_or(data["prefix"])(bot, message)
    except:
        return commands.when_mentioned_or(bot.DEFAULTPREFIX)(bot, message)


bot = commands.Bot(
    command_prefix=get_prefix,
    case_insensitive=True,
    owner_id=271612318947868673,
    description="A bot designed for showcasing DPY",
    help_command=None,
)

bot.DEFAULTPREFIX = DEFAULTPREFIX
bot.news_api_key = secret_file["news api"]
bot.main_channel_id = int(secret_file["main channel"])
bot.colors = {
    "WHITE": 0xFFFFFF,
    "AQUA": 0x1ABC9C,
    "GREEN": 0x2ECC71,
    "BLUE": 0x3498DB,
    "PURPLE": 0x9B59B6,
    "LUMINOUS_VIVID_PINK": 0xE91E63,
    "GOLD": 0xF1C40F,
    "ORANGE": 0xE67E22,
    "RED": 0xE74C3C,
    "NAVY": 0x34495E,
    "DARK_AQUA": 0x11806A,
    "DARK_GREEN": 0x1F8B4C,
    "DARK_BLUE": 0x206694,
    "DARK_PURPLE": 0x71368A,
    "DARK_VIVID_PINK": 0xAD1457,
    "DARK_GOLD": 0xC27C0E,
    "DARK_ORANGE": 0xA84300,
    "DARK_RED": 0x992D22,
    "DARK_NAVY": 0x2C3E50,
}
bot.color_list = [c for c in bot.colors.values()]


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name=bot.description))

    # Init db
    bot.db = motor.motor_asyncio.AsyncIOMotorClient(secret_file["mongo"]).pythonMeetup
    bot.config = Document(bot.db, "config")
    bot.command_usage = Document(bot.db, "command usage")

    for document in await bot.config.get_all():
        print(document)

    print(f"{bot.user.name} is connected and ready to rock n roll!\n-----")


@bot.event
async def on_command_completion(ctx):
    if await bot.command_usage._Document__get_raw(ctx.command.qualified_name) == None:
        await bot.command_usage.upsert(
            {"_id": ctx.command.qualified_name, "usage count": 1}
        )
    else:
        await bot.command_usage.increment(ctx.command.qualified_name, 1, "usage count")


@bot.event
async def on_command_error(ctx, error):
    # If I ran the command, just send me the whole error
    if ctx.author.id == bot.owner_id and not isinstance(
        error, commands.CommandOnCooldown
    ):
        if ctx.command:
            await SendEmbed(
                bot, ctx, f"An error occured in `{ctx.command.name}`", error
            )
            raise error
            return

    # Ignore these errors
    ignored = commands.CommandNotFound  # , commands.UserInputError)
    if isinstance(error, ignored):
        return

    if isinstance(error, commands.CommandOnCooldown):
        # If the command is currently on cooldown trip this
        m, s = divmod(error.retry_after, 60)
        h, m = divmod(m, 60)
        if int(h) == 0 and int(m) == 0:
            await ctx.send(f" You must wait {int(s)} seconds to use this command!")
        elif int(h) == 0 and int(m) != 0:
            await ctx.send(
                f" You must wait {int(m)} minutes and {int(s)} seconds to use this command!"
            )
        else:
            await ctx.send(
                f" You must wait {int(h)} hours, {int(m)} minutes and {int(s)} seconds to use this command!"
            )
    elif isinstance(error, commands.PrivateMessageOnly):
        await ctx.send("Hey! This command must be used in dms.")
    elif isinstance(error, commands.NoPrivateMessage):
        await ctx.send("Hey! This command must not be used in dms.")
    elif isinstance(error, commands.DisabledCommand):
        await ctx.send("This command is currently disabled.")
    elif isinstance(error, commands.MaxConcurrencyReached):
        await ctx.send(
            "This guild has too many of this command running already, please wait for them to end before trying again."
        )
    elif isinstance(error, commands.NotOwner):
        await ctx.send("You do not own this bot, therefore you cannot do this.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send(
            f"You lack permissions to run this command.\nPermissions needed: `{error.missing_perms[0]}`"
        )
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send("The bot lacks the permissions to run this command.")
    elif isinstance(error, commands.NSFWChannelRequired):
        await ctx.send("This command requires a nsfw channel.")
    elif isinstance(error, commands.BadUnionArgument):
        await ctx.send("Internal conversion error. Please retry with different inputs.")
    elif isinstance(error, commands.UserInputError):
        arg = error.param
        await ctx.send(
            f"This command needs more arguments, please provide `{arg}` when calling the command.\nAlternatively look at the help command for this category of commands."
        )

    raise error


@bot.event
async def on_message(message):
    # Ignore messages sent by bots
    if message.author.bot:
        return

    # Whenever the bot is tagged, respond with its prefix
    if match := mention.match(message.content):
        if int(match.group("id")) == bot.user.id:
            data = await bot.config._Document__get_raw(message.guild.id)
            if not data or "prefix" not in data:
                prefix = bot.DEFAULTPREFIX
            else:
                prefix = data["prefix"]
            await message.channel.send(f"My prefix here is `{prefix}`", delete_after=15)

    await bot.process_commands(message)


extensions = ["cogs.help", "cogs.config", "cogs.reminder"]
if __name__ == "__main__":
    # Manual extension loading
    for extension in extensions:
        try:
            bot.load_extension(extension)
            print(f"Loaded {extension}")
        except Exception as e:
            print(f"Failed to load extension {extension}.", file=sys.stderr)
            traceback.print_exc()

    # Automatic extension loading
    # for ext in os.listdir("./cogs/"):
    #     if ext.endswith(".py") and not ext.startswith("_"):
    #         try:
    #             bot.load_extension(f"cogs.{ext[:-3]}")
    #         except Exception as e:
    #             print(
    #                 f"An error occurred while loading extension: cogs.{ext[:-3]}, {repr(e)}"
    #            )

    # Actually start our bot
    bot.run(secret_file["token"])

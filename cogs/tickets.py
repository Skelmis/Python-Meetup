import discord
from discord.ext import commands

from utils.util import (
    CreateNewTicket,
    SudoCreateNewTicket,
    CloseTicket,
    CheckIfTicket,
    ReactionCreateNewTicket,
    SetupNewTicketMessage,
    CheckIfValidReactionMessage,
    ReactionCloseTicket,
)
from utils.jsonLoader import read_json


class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} cog has been loaded\n-----")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        bot = self.bot
        # Check if its the bot adding the reaction
        if payload.user_id == bot.user.id:
            return

        # Check if its a valid reaction
        reaction = str(payload.emoji)
        if reaction not in ["🔒", "✅"]:
            return

        # Check its a valid reaction channel
        if not payload.channel_id == bot.new_ticket_channel_id and not CheckIfTicket(
            str(payload.channel_id)
        ):
            return

        # Check its a valid message
        if not CheckIfValidReactionMessage(payload.message_id):
            return

        data = read_json("config")
        if payload.message_id == data["ticketSetupMessageId"] and reaction == "✅":
            # We want a new ticket...
            await ReactionCreateNewTicket(bot, payload)

            # once the ticket is created remove the user reaction
            guild = bot.get_guild(payload.guild_id)
            member = await guild.fetch_member(payload.user_id)

            channel = bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            await message.remove_reaction("✅", member)
            return

        elif reaction == "🔒":
            # Simply add a tick to the message
            channel = bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            await message.add_reaction("✅")

        elif reaction == "✅":
            # Time to delete the ticket!
            guild = bot.get_guild(payload.guild_id)
            member = await guild.fetch_member(payload.user_id)

            channel = bot.get_channel(payload.channel_id)
            await ReactionCloseTicket(bot, channel, member)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        bot = self.bot
        # Check if its the bot adding the reaction
        if payload.user_id == bot.user.id:
            return

        # Check if its a valid reaction
        reaction = str(payload.emoji)
        if reaction not in ["🔒"]:
            return

        # Check its a valid reaction channel
        if not payload.channel_id == bot.new_ticket_channel_id and not CheckIfTicket(
            str(payload.channel_id)
        ):
            return

        # Check its a valid message
        if not CheckIfValidReactionMessage(payload.message_id):
            return

        if reaction == "🔒":
            # Simply remove a tick from the message
            guild = bot.get_guild(payload.guild_id)
            member = await guild.fetch_member(bot.user.id)

            channel = bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            await message.remove_reaction("✅", member)

    @commands.command(
        name="new", description="Create a new ticket", usage="[Ticket Subject]"
    )
    async def new(self, ctx, *, subject=None):
        await CreateNewTicket(self.bot, ctx, subject)

    @commands.command(name="close", description="Close this ticket", usage="[Reason]")
    async def close(self, ctx, *, reason=None):
        await CloseTicket(self.bot, ctx, reason)

    @commands.command(
        name="sudonew",
        description="For creating a ticket on behalf of a user",
        usage="<User>",
    )
    @commands.is_owner()
    async def sudonew(self, ctx, user: discord.Member):
        await ctx.message.delete()
        await SudoCreateNewTicket(self.bot, ctx.guild, user, ctx.message)

    @commands.command(name="setup", description="Setup the reactions for tickets")
    @commands.is_owner()
    async def setup(self, ctx):
        await SetupNewTicketMessage(self.bot)


def setup(bot):
    bot.add_cog(Config(bot))

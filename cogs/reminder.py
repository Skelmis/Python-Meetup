import re
import asyncio

import discord
from discord.ext import commands

time_regex = re.compile(r"(?:(\d{1,5})([hsmd]))+?")
time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400}


class TimeConverter(commands.Converter):
    async def convert(self, ctx, argument):
        args = argument.lower()
        matches = re.findall(time_regex, args)
        time = 0
        for key, value in matches:
            try:
                time += time_dict[value] * float(key)
            except KeyError:
                raise commands.BadArgument(
                    f"{value} is an invalid time key! h|m|s|d are valid arguments"
                )
            except ValueError:
                raise commands.BadArgument(f"{key} is not a number!")
        return round(time)


class Reminder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} cog has been loaded\n-----")

    @commands.command(
        name="reminder",
        aliases=["remind", "remindme"],
        description="Use this to remind yourself!",
        usage="<time> [message]",
    )
    async def reminder(self, ctx, time: TimeConverter, *, message):
        """
        :param time: Matches a single time item out of hours, minutes, seconds, days
        """
        await ctx.send(
            f"Hey {ctx.author.mention}, I will remind you soon!", delete_after=30
        )
        await asyncio.sleep(int(time))

        embed = discord.Embed(
            title=f"Reminder for {ctx.author.display_name}",
            description=message,
            timestamp=ctx.message.created_at,
        )
        embed.set_footer(text="Reminder from")
        await ctx.send(f"{ctx.author.mention}", embed=embed)


def setup(bot):
    bot.add_cog(Reminder(bot))

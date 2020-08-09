import discord
from discord.ext import commands


class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def our_custom_check():
        async def predicate(ctx):
            return (
                ctx.guild is not None
                and ctx.author.guild_permissions.manage_channels
                and ctx.me.guild_permissions.manage_channels
            )

        return commands.check(predicate)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} cog has been loaded\n-----")

    @commands.command(
        name="prefix",
        aliases=["changeprefix", "setprefix"],
        description="Change your guilds prefix!",
        usage="[prefix]",
    )
    @commands.cooldown(1, 10, commands.BucketType.guild)
    @commands.has_guild_permissions(manage_guild=True)
    async def prefix(self, ctx, *, prefix=None):
        prefix = prefix or self.bot.DEFAULTPREFIX
        await self.bot.config.upsert({"_id": ctx.guild.id, "prefix": prefix})
        await ctx.send(
            f"The guild prefix has been set to `{prefix}`. Use `{prefix}prefix [prefix]` to change it again!"
        )

    @commands.command(
        name="purge",
        description="A command which purges the given channel",
        usage="[Amount]",
    )
    @our_custom_check()
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def purge(self, ctx, amount=15):
        await ctx.channel.purge(limit=amount + 1)

        embed = discord.Embed(
            title=f"{ctx.author.name} purged: {ctx.channel.name}",
            description=f"{amount} messages were cleared",
        )
        await ctx.send(embed=embed, delete_after=15)


def setup(bot):
    bot.add_cog(Config(bot))

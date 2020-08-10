import discord
from git import Repo
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

    @commands.command(
        name="reload", description="Reload all/one of the bots cogs!", usage="[cog]",
    )
    @commands.is_owner()
    async def reload(self, ctx, cog=None):
        if not cog:
            async with ctx.typing():
                embed = discord.Embed(
                    title="Reloading all cogs!",
                    color=0x808080,
                    timestamp=ctx.message.created_at,
                )
                for ext in os.listdir("./cogs/"):
                    if ext.endswith(".py") and not ext.startswith("_"):
                        try:
                            self.bot.unload_extension(f"cogs.{ext[:-3]}")
                            await asyncio.sleep(0.5)
                            self.bot.load_extension(f"cogs.{ext[:-3]}")
                            embed.add_field(
                                name=f"Reloaded: `{ext}`",
                                value=f"`{ext}` reloaded, but what did you expect to happen? Like really..",
                            )
                        except Exception as e:
                            embed.add_field(
                                name=f"Failed to reload: `{ext}`", value=e,
                            )
                    await asyncio.sleep(0.5)
                await ctx.send(embed=embed)
        else:
            async with ctx.typing():
                embed = discord.Embed(
                    title=f"Reloading {cog}!",
                    color=0x808080,
                    timestamp=ctx.message.created_at,
                )
                cog = cog.lower()
                ext = f"{cog}.py"
                if not os.path.exists(f"./cogs/{ext}"):
                    embed.add_field(
                        name=f"Failed to reload: `{ext}`",
                        value="This cog file does not exist.",
                    )
                elif ext.endswith(".py") and not ext.startswith("_"):
                    try:
                        self.bot.unload_extension(f"cogs.{ext[:-3]}")
                        await asyncio.sleep(0.5)
                        self.bot.load_extension(f"cogs.{ext[:-3]}")
                        embed.add_field(
                            name=f"Reloaded: `{ext}`",
                            value=f"`{ext}` reloaded, but what did you expect to happen? Like really..",
                        )
                    except Exception:
                        desired_trace = traceback.format_exc()
                        embed.add_field(
                            name=f"Failed to reload: `{ext}`", value=desired_trace,
                        )
                await asyncio.sleep(0.5)
            await ctx.send(embed=embed)

    @commands.command(
        name="update", description="Automatically updates the bot from github!",
    )
    @commands.is_owner()
    async def update_bot(self, ctx):
        async with ctx.typing():
            repo = Repo(os.getcwd())
            repo.git.checkout(
                "development"
            )  # Make sure to be on right branch before pulling it
            repo.git.fetch()
            repo.git.pull()

            # attempt to reload all commands
            await self.reload(ctx)


def setup(bot):
    bot.add_cog(Config(bot))

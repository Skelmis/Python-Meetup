import logging

import discord
from libneko import pag
from discord.ext import commands


class Help(commands.Cog, name="Help command"):
    def __init__(self, bot):
        self.bot = bot
        self.cmds_per_page = 6

    def get_command_signature(self, command: commands.Command, ctx: commands.Context):
        parent = command.full_parent_name
        if len(command.aliases) > 0:
            aliases = "|".join(command.aliases)
            cmd_invoke = f"[{command.name}|{aliases}]"
            signature = (
                f"{ctx.prefix}{cmd_invoke} {command.signature if command.signature else ''}"
                if not parent
                else f"{ctx.prefix}{parent} {cmd_invoke} {command.signature if command.signature else ''}"
            )
            return signature
        else:
            signature = (
                f"{ctx.prefix}{command.name} {command.signature if command.signature else ''}"
                if not parent
                else f"{ctx.prefix}{parent} {command.name} {command.signature if command.signature else ''}"
            )
            return signature

    async def return_filtered_commands(self, walkable, ctx):
        filtered = []

        for c in walkable.walk_commands():
            try:
                if c.hidden:
                    # command is hidden
                    continue

                elif c.parent != None:
                    # Command is a subcommand
                    continue

                await c.can_run(ctx)
                filtered.append(c)
            except:
                continue

        return filtered

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    @commands.command(
        name="help", aliases=["h", "commands"], description="The help command!"
    )
    async def help_command(self, ctx, *, entity=None):
        """
        Sends a paginated help command or help for
        an existing entity.
    	"""
        # Inspired by nekozilla
        if not entity:

            embeds = []

            filtered_commands = await self.return_filtered_commands(self.bot, ctx)

            for i in range(0, len(filtered_commands), self.cmds_per_page):

                embed_page = discord.Embed(
                    title="Command List",
                    description=self.bot.description,
                    colour=0xCE2029,
                )

                next_commands = filtered_commands[i : i + self.cmds_per_page]

                for cmd in next_commands:
                    cmd: commands.Command = cmd

                    embed_page.add_field(
                        name=cmd.name,
                        value=f"{cmd.description or 'No description'}\n{'Has subcommands' if hasattr(cmd, 'all_commands') else ''}",
                        inline=False,
                    )

                embeds.append(embed_page)

            pag.EmbedNavigator(pages=embeds, ctx=ctx).start()

        else:
            cog = self.bot.get_cog(entity)
            if cog:
                embeds = []
                filtered_commands = await self.return_filtered_commands(cog, ctx)

                for i in range(0, len(filtered_commands), self.cmds_per_page):

                    embed_page = discord.Embed(
                        title=cog.qualified_name, colour=0xCE2029
                    )

                    next_commands = filtered_commands[i : i + self.cmds_per_page]

                    for cmd in next_commands:

                        embed_page.add_field(
                            name=cmd.qualified_name,
                            value=(cmd.description or "No description"),
                            inline=False,
                        )

                    embeds.append(embed_page)
                pag.EmbedNavigator(pages=embeds, ctx=ctx).start()
            else:
                command = self.bot.get_command(entity)
                if command:
                    embeds = []
                    embed = discord.Embed(
                        title="Help command",
                        description=f"```{self.get_command_signature(command, ctx)}```\n{command.description or 'No description.'}",
                        colour=0xCE2029,
                    )
                    if command.all_commands:
                        for i in range(
                            0,
                            len(list(command.all_commands.values())),
                            self.cmds_per_page,
                        ):
                            next_commands = filtered_commands[
                                i : i + self.cmds_per_page
                            ]

                            for cmd in next_commands:
                                embed.add_field(
                                    name=cmd.name,
                                    value=f"```\n{self.get_command_signature(cmd, ctx)}\n```\n{cmd.description or 'No description'}",
                                )

                        embeds.append(embed)
                    pag.EmbedNavigator(pages=embeds, ctx=ctx).start()
                else:
                    await ctx.send("Entity not found.")


def setup(bot):
    bot.add_cog(Help(bot))

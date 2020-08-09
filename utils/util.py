import random

import discord


async def SendEmbed(bot, ctx, contentOne="Default Message", contentTwo="\uFEFF"):
    """
    Simply sends a nice embed

    Params:
     - bot (commands.Bot object) :
     - ctx (context object) : Used for sending msgs n stuff

     - Optional Params:
        - contentOne (string) : Embed title
        - contentTwo (string) : Embed description
    """
    embed = discord.Embed(
        title=f"{contentOne}",
        description=f"{contentTwo}",
        colour=random.choice(bot.color_list),
    )
    await ctx.send(embed=embed, delete_after=100)

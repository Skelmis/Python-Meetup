import discord
from aiohttp import ClientSession
from discord.ext import commands, tasks


class News(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} cog has been loaded\n-----")

    @commands.command()
    async def news(self, ctx):
        url = f"https://newsapi.org/v2/top-headlines?country=nz&apiKey={self.bot.news_api_key}"
        async with ClientSession() as session:
            async with session.get(url) as response:
                r = await response.json()
                firstArticle = r["articles"][0]
                nSource = firstArticle["source"]["name"]
                nTitle = firstArticle["title"]
                nTimestamp = firstArticle["publishedAt"]
                embed = discord.Embed(
                    title=f"News Title: {nTitle}", description=f"News Source: {nSource}"
                )
                embed.add_field(name="News Content", value=firstArticle["description"])
                embed.set_image(url=firstArticle["urlToImage"])
                embed.set_footer(text=f"News Timestamp: {nTimestamp}")
                await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(News(bot))

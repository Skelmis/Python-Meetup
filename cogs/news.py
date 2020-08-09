import discord
from aiohttp import ClientSession
from discord.ext import commands, tasks


class News(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.news_task = self.news.start()

    def unload(self):
        self.news_task.stop()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} cog has been loaded\n-----")

    @tasks.loop(hours=6)
    async def news(self):
        """
        Send the first news article every 6 hours for nz from the given url
        :return:
        """
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

                channel = self.bot.get_channel(self.bot.main_channel_id)
                await channel.send(embed=embed)

    @news.before_loop
    async def before_news(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(News(bot))

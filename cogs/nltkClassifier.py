import discord
from discord.ext import commands

from utils.classifier import Classifier


class NltkClassifier(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.classifier = Classifier()

    @commands.Cog.listener()
    async def on_ready(self):
        self.classifier.start()
        print(f"{self.__class__.__name__} cog has been loaded\n-----")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        response = self.classifier.classify(message.content)
        print(response)
        if response is not None:
            await message.channel.send(response)


def setup(bot):
    bot.add_cog(NltkClassifier(bot))

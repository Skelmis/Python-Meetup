import asyncio

import discord
from gtts import gTTS
from discord.ext import commands


class GTTS(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} cog has been loaded\n-----")

    @commands.command()
    async def connect(self, ctx, *, channel: discord.VoiceChannel = None):
        """
        Connect to a voice channel
        This command also handles moving the bot to different channels.

        Params:
        - channel: discord.VoiceChannel [Optional]
            The channel to connect to. If a channel is not specified, an attempt to join the voice channel you are in
            will be made.
        """
        if not channel:
            try:
                channel = ctx.author.voice.channel
            except AttributeError:
                raise InvalidVoiceChannel(
                    "No channel to join. Please either specify a valid channel or join one."
                )

        vc = ctx.voice_client

        if vc:
            if vc.channel.id == channel.id:
                return
            try:
                await vc.move_to(channel)
            except asyncio.TimeoutError:
                raise discord.VoiceConnectionError(
                    f"Moving to channel: <{channel}> timed out."
                )
        else:
            try:
                await channel.connect()
            except asyncio.TimeoutError:
                raise discord.VoiceConnectionError(
                    f"Connecting to channel: <{channel}> timed out."
                )

        await ctx.send(f"Connected to: **{channel}**", delete_after=20)

    @commands.command()
    async def disconnect(self, ctx):
        """
        Disconnect from a voice channel, if in one
        """
        vc = ctx.voice_client

        if not vc:
            await ctx.send("I am not in a voice channel.")
            return

        await vc.disconnect()
        await ctx.send("I have left the voice channel!")

    @commands.command()
    async def repeat(self, ctx, *, text=None):
        """
        A command which saves `text` into a speech file with
        gtts and then plays it back in the current voice channel.

        Params:
         - text [Optional]
            This will be the text we speak in the voice channel
        """
        if not text:
            # We have nothing to speak
            await ctx.send(
                f"Hey {ctx.author.mention}, I need to know what to say please."
            )
            return

        await ctx.send("Preparing...", delete_after=5)

        vc = ctx.voice_client  # We use it more then once, so make it an easy variable
        if not vc:
            # We are not currently in a voice channel
            await ctx.send(
                "I need to be in a voice channel to do this, please use the connect command."
            )
            return

        # Lets prepare our text, and then save the audio file
        tts = gTTS(text=text)
        tts.save("assets/text.mp3")

        try:
            # Lets play that mp3 file in the voice channel
            vc.play(
                discord.FFmpegPCMAudio("assets/text.mp3"),
                after=lambda e: print(f"Finished playing: {e}"),
            )

            # Lets set the volume to 1
            vc.source = discord.PCMVolumeTransformer(vc.source)
            vc.source.volume = 1

        # Handle the exceptions that can occur
        except discord.ClientException as e:
            await ctx.send(f"A client exception occured:\n`{e}`")
        except TypeError as e:
            await ctx.send(f"TypeError exception:\n`{e}`")
        except discord.OpusNotLoaded as e:
            await ctx.send(f"OpusNotLoaded exception: \n`{e}`")


def setup(bot):
    bot.add_cog(GTTS(bot))

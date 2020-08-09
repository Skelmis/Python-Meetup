import discord
from discord.ext import commands
from aiohttp import ClientSession


class Covid(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} cog has been loaded\n-----")

    @commands.command(
        name="covid",
        description="Gets information of Covid-19 stats of a country",
        usage="<country>",
    )
    async def covid(self, ctx, country=None):
        if not country:
            await ctx.send("Please specify a country to get info for!")
            return

        url = f"https://disease.sh/v3/covid-19/countries/{country}"
        async with ClientSession() as session:
            async with session.get(url) as response:
                data = [await response.json()]

                # getting data from API then format to readable numbers
                test = data[0]["countryInfo"]["flag"]
                population = data[0]["population"]
                population_format = format(data[0]["population"], ",")
                country = data[0]["country"]
                cases = data[0]["cases"]
                cases_format = format(cases, ",")
                today_cases = data[0]["todayCases"]
                today_cases_format = format(today_cases, ",")
                deaths = data[0]["deaths"]
                deaths_format = format(deaths, ",")
                active = data[0]["active"]
                active_format = format(active, ",")
                today_deaths = data[0]["todayDeaths"]
                recovered = data[0]["recovered"]
                recovered_format = format(recovered, ",")
                critical = data[0]["critical"]
                critical_format = format(critical, ",")
                tests = data[0]["tests"]
                tests_format = format(tests, ",")

                # making stats
                fatality = f"{round(deaths / cases * 100, 2)}%"
                infected = f"{round(cases / population * 100, 2)}%"
                critical_rate = f"{round(critical / active * 100, 2)}%"
                recovered_rate = f"{round(recovered / cases * 100, 2)}%"
                test_rate = f"{round(tests / population * 100, 2)}%"

                # making embed
                embed = discord.Embed(title=f"Covid Details: {country}")
                embed.set_thumbnail(url=test)
                embed.add_field(name="Total Cases", value=cases_format + "\u200b")
                embed.add_field(name="Total Deaths", value=deaths_format)
                embed.add_field(name="Active", value=active_format)
                embed.add_field(name="Recovered", value=recovered_format)
                embed.add_field(name="Critical", value=critical_format)
                embed.add_field(name="Tests", value=tests_format)
                embed.add_field(name="Population", value=population_format)
                embed.add_field(name="Infection Rate", value=infected)
                embed.add_field(name="Fatality Rate", value=fatality)
                embed.add_field(name="Critical Rate", value=critical_rate)
                embed.add_field(name="Recovery Rate", value=recovered_rate)
                embed.add_field(name="Test Rate", value=test_rate)
                await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Covid(bot))

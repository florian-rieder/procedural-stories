import discord
from discord.ext import commands


class UtilCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="ping")
    async def ping(self, ctx: commands.Context[commands.Bot]) -> None:
        """Pong!"""
        print("Pong!")
        await ctx.reply("Pong!")

    @commands.hybrid_command(name="uptime")
    async def uptime(self, ctx: commands.Context[commands.Bot]) -> None:
        """Pong!"""
        await ctx.reply(self.bot.uptime)

    @commands.hybrid_command(name="echo")
    async def echo(self, ctx: commands.Context[commands.Bot], message: str):
        """
        Echoes a message

        Parameters
        ----------
        ctx: commands.Context
            The context of the command invocation
        message: str
            The message to echo
        """
        await ctx.reply(message)


async def setup(bot: commands.Bot):
    await bot.add_cog(UtilCog(bot))


async def teardown(bot: commands.Bot):
    # print(f"{__name__} unloaded!")
    pass

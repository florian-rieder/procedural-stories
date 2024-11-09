import discord
from discord.ext import commands


class ChatCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.started = False

    @commands.hybrid_command(name="reset")
    async def reset(self, ctx: commands.Context[commands.Bot]) -> None:
        await ctx.defer()  # Acknowledge the command to prevent timeout
        self.bot.chain.memory.clear()
        await ctx.reply('Memory cleared !')

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

    @commands.hybrid_command(name="start")
    async def start(self, ctx: commands.Context[commands.Bot]):
        """
        Start an adventure
        """
        self.started = True
        
        # Reply with the start scene
        await ctx.reply("Adventure started !")

    @commands.Cog.listener("on_message")
    async def on_message(self, message: discord.Message):
        if not self.started:
            return

        # Basic debug prints to see if the event is firing
        print('Event triggered! Message content:', message.content)

        # Avoid the bot responding to its own messages
        if message.author == self.bot.user:
            return

        # Ensure the bot can still process commands
        await self.bot.process_commands(message)

        # Notify user that the bot is processing by showing "typing..."
        async with message.channel.typing():
            # Simulate some processing time if needed
            response = await self.bot.chain.ainvoke(message.content)

        # Send the LLM response in the channel
        await message.channel.send(response['response'])


async def setup(bot: commands.Bot):
    await bot.add_cog(ChatCog(bot))


async def teardown(bot: commands.Bot):
    # print(f"{__name__} unloaded!")
    pass

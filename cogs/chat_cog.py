import discord
from discord.ext import commands

# Trivial system
from generator.trivial import get_chain as get_trivial_chain
# Our system
from generator.story import get_chain as get_story_chain


first_message = """
Tu te trouves au coeur de la Forêt Abandonnée, un lieu où la nature a repris son droit après avoir été dévastée par l'épidémie zombie. Les arbres gémissent sous le vent, leurs branches cassantes semblent menaçantes, tandis que les feuilles mortes crissent sous tes pieds. La lumière filtrant entre les feuilles forme des motifs étranges sur le sol, créant une atmosphère mystérieuse.

Tu es Alexandre Durand, un ancien biologiste spécialisé dans les maladies virales. Tu as été choisi pour explorer les zones contaminées alentour du Village des Survivants, là où ta famille t'attend. Le but de ton voyage est simple : trouver une source sécurisée de nourriture ou d'eau potable pour assurer la survie immédiate du Village. Sans ces éléments vitaux, tout ce que tu feras sera vain.

La Forêt Abandonnée semble être un bon début. On dit qu'elle abrite encore quelques sources d'eau pure, ainsi que des plantes médicinales capables de guérir les blessures. Mais attention, tu n'es pas seul ici. D'autres personnes ont également trouvé refuge dans cet endroit hostile, chacun poursuivant leurs objectifs secrets... 

Que fais-tu maintenant?
"""


class ChatCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.started = False
        self.setting = "Post-apocalypse zombie mondiale, 1 an après le début de l'épidémie"
        self.language = "french"
        self.first_message = first_message
        
        
        # Initialize LLM pipeline
        self.trivial_chain = get_trivial_chain(self.bot.model, self.first_message)
        #self.story_chain = get_story_chain()


    @commands.hybrid_command(name="reset")
    async def reset(self, ctx: commands.Context[commands.Bot]) -> None:
        await ctx.defer()  # Acknowledge the command to prevent timeout
        self.bot.chain.memory.clear()
        await ctx.reply('Memory cleared !')

    @commands.hybrid_command(name="start")
    async def start(self, ctx: commands.Context[commands.Bot]):
        """
        Start an adventure
        """
        self.started = True

        # Reply with the start scene
        await ctx.reply("Commençons l'aventure !\n" + self.first_message)
    
    @commands.hybrid_command(name="stop")
    async def stop(self, ctx: commands.Context[commands.Bot]):
        """
        Start an adventure
        """
        self.started = False

        # Reply with the start scene
        await ctx.reply("Merci d'avoir joué !")


    @commands.Cog.listener("on_message")
    async def on_message(self, message: discord.Message):
        if not self.started:
            return

        # Basic debug prints to see if the event is firing
        print('Event triggered! Message content:', message.content)

        # Avoid the bot responding to its own messages
        if message.author == self.bot.user:
            return

        if message.content.startswith('!') or message.content.startswith('/'):
            return
        # Ensure the bot can still process commands
        #await self.bot.process_commands(message)

        # Notify user that the bot is processing by showing "typing..."
        async with message.channel.typing():
            # Send the message to the procedural story system
            response = await self.trivial_chain(
                {
                    "setting": self.setting,
                    "language": self.language,
                    "message": message.content
                },
                config={"configurable": {"session_id": message.author}}
            )

        # Send the LLM response in the channel
        await message.channel.send(response.content)


async def setup(bot: commands.Bot):
    await bot.add_cog(ChatCog(bot))


async def teardown(bot: commands.Bot):
    # print(f"{__name__} unloaded!")
    pass

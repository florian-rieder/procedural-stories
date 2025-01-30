import random
import os
import logging
import discord
from discord.ext import commands


from generator.trivial.converse import TrivialConverse
from generator.story.converse import StoryConverse

logger = logging.getLogger(__name__)
first_message = "Vous vous trouvez dans la ville royale, au cœur d'un royaume médiéval fantastique où les chevaliers et les mages règnent en maîtres. Vous êtes un aventurier courageux et déterminé, issu d'une famille de chevaliers, avec une quête personnelle de sauver le monde des Ténèbres. Une force obscure s'est levée, menaçant de détruire l'équilibre du monde, et vous avez appris qu'il existe trois artefacts anciens capables de vaincre cette menace. L'un de ces artefacts, une pierre lumineuse, se trouve quelque part dans la ville, gardée par des dangers et des mystères. Vous ressentez un fort sentiment de responsabilité et de devoir envers votre famille et votre royaume, et vous êtes prêt à affronter les défis qui vous attendent pour récupérer ces artefacts et sauver le monde des Ténèbres. La ville royale est en effervescence, les marchés sont animés et les tavernes bruyantes, mais vous savez que vous devez agir vite, car la nuit tombe déjà et les forces des ténèbres ne tarderont pas à se manifester."


class ChatCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.started = False
        self.setting = "Un jeu de rôle médiéval fantastique, dans la veine de Zork."
        self.start_ontology_file = "worlds/story_world_fantasy_used_for_testing.rdf"
        self.language = "french"
        self.first_message = first_message
        self.current_chain = None

        self.story_converse = StoryConverse(
            self.bot.model,
            self.bot.predictable_model,
            self.first_message,
            self.setting,
            self.language,
            self.start_ontology_file,
            "foo",
        )

        self.trivial_converse = TrivialConverse(
            self.bot.model,
            self.first_message,
            self.setting,
            self.language,
            "foo",
        )

        self.current_chain = self.story_converse

    # Define a command to choose between trivial and story mode
    @commands.hybrid_command(name="set_mode")
    async def set_mode(
        self, ctx: commands.Context[commands.Bot], mode: str, session_id: str
    ):
        await ctx.defer()  # Acknowledge the command to prevent timeout
        try:
            if mode == "trivial":
                self.current_chain = self.trivial_converse
            elif mode == "story":
                self.current_chain = self.story_converse
        except Exception as e:
            await ctx.reply(f"Error setting mode: {e}")
            return

        await ctx.reply(f"Set mode to {mode} with session id {session_id}!")

    @commands.hybrid_command(name="start_experiment")
    async def start_experiment(
        self,
        ctx: commands.Context[commands.Bot],
    ):
        await ctx.defer()  # Acknowledge the command to prevent timeout
        # Create a directory for the user if it doesn't exist
        os.makedirs(f"data/{ctx.channel.name}", exist_ok=True)

        # Record which mode we're starting with
        self.is_trivial_mode = random.random() < 0.5

        if self.is_trivial_mode:
            print("Starting with trivial mode (A/B)")
            self.current_chain = self.trivial_converse
        else:
            print("Starting with story mode (B/A)")
            self.current_chain = self.story_converse

        # Record the model order in the user's data directory
        with open(f"data/{ctx.channel.name}/model_order.txt", "w") as f:
            f.write(f"{'A/B' if self.is_trivial_mode else 'B/A'}")

        self.started = True

        await ctx.reply("Commençons l'aventure !\n" + self.first_message)

    @commands.hybrid_command(name="switch_mode")
    async def switch_mode(self, ctx: commands.Context[commands.Bot]):
        """Switch to the other experimental mode"""

        with open(f"data/{ctx.channel.name}/model_order.txt", "r") as f:
            order = f.read().strip()

        if order == "A/B":
            print("Switching to story mode (A/B)")
            self.current_chain = self.story_converse
        else:
            print("Switching to trivial mode (B/A)")
            self.current_chain = self.trivial_converse

        self.started = True

        await ctx.reply("Mode switched!\n" + self.first_message)

    @commands.hybrid_command(name="reset")
    async def reset(self, ctx: commands.Context[commands.Bot]) -> None:
        await ctx.defer()  # Acknowledge the command to prevent timeout
        self.current_chain.reset()
        await ctx.reply("Memory cleared !")

    @commands.hybrid_command(name="start")
    async def start(self, ctx: commands.Context[commands.Bot]):
        """
        Start an adventure
        """
        await ctx.defer()  # Acknowledge the command to prevent timeout

        # Check if a chain is initialized
        if self.current_chain is None:
            await ctx.reply("No chain initialized. Please set a mode first.")
            return

        self.started = True

        # Reply with the start scene
        await ctx.reply("Commençons l'aventure !\n" + self.first_message)

    @commands.hybrid_command(name="stop")
    async def stop(self, ctx: commands.Context[commands.Bot]):
        """
        Start an adventure
        """
        await ctx.defer()  # Acknowledge the command to prevent timeout
        self.started = False

        # Reply with the start scene
        await ctx.reply("Merci d'avoir joué !")

    @commands.Cog.listener("on_message")
    async def on_message(self, message: discord.Message):
        if not self.started:
            return

        # Basic debug prints to see if the event is firing
        # print('Event triggered! Message content:', message.content)

        # Avoid the bot responding to its own messages
        if message.author == self.bot.user:
            return

        if message.content.startswith("!") or message.content.startswith("/"):
            return
        # Ensure the bot can still process commands
        # await self.bot.process_commands(message)

        # Notify user that the bot is processing by showing "typing..."
        async with message.channel.typing():
            # Send the message to the procedural story system
            response = await self.current_chain.converse(message.content)

        # Send the LLM response in the channel
        await message.channel.send(response)

        # Do post-processing after the reply
        await self.current_chain.postprocess_last_turn()


async def setup(bot: commands.Bot):
    await bot.add_cog(ChatCog(bot))


async def teardown(bot: commands.Bot):
    # print(f"{__name__} unloaded!")
    pass

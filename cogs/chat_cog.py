import random
import os
import logging
import discord
from discord.ext import commands


from generator.trivial.converse import TrivialConverse
from generator.story.converse import StoryConverse

logger = logging.getLogger(__name__)
first_message = "Vous vous trouvez dans une communauté isolée, barricadée et surveillée, où quelques dizaines de survivants comme vous ont trouvé refuge. Vous avez perdu des proches lors de l'épidémie et vous êtes déterminé à trouver un moyen de vaincre les Errants et de reconstruire votre monde. Vous avez reçu une mission, et vous savez que votre seul espoir de survie réside dans la découverte d'un remède contre l'épidémie. Vous devez partir à la recherche d'informations sur ce remède, mais pour cela, vous devrez quitter la sécurité relative de votre communauté et affronter les dangers du monde extérieur."



class ChatCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.started = False
        self.setting = "Post-apocalypse zombie mondiale, 1 an après le début de l'épidémie"
        self.start_ontology_file = "story_poptest70b.rdf"
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
            'foo', 
        )

        self.trivial_converse = TrivialConverse(
            self.bot.model,
            self.first_message, 
            self.setting, 
            self.language,
            'foo', 
        )

        self.current_chain = self.story_converse

    
    # Define a command to choose between trivial and story mode
    @commands.hybrid_command(name="set_mode")
    async def set_mode(self, ctx: commands.Context[commands.Bot], mode: str, session_id: str):
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



    # Variant for double blind experiment: the user and experimenter don't know which mode they are in. We need to choose the model randomly and add another command to switch to the other mode, while recording the actual mode used.
    @commands.hybrid_command(name="start_experiment")
    async def start_experiment(self, ctx: commands.Context[commands.Bot], session_id: str):
        await ctx.defer()  # Acknowledge the command to prevent timeout
        # Create a directory for the user if it doesn't exist
        os.makedirs(f'data/{session_id}', exist_ok=True)

        # Record which mode we're starting with
        self.is_trivial_mode = random.random() < 0.5
        
        if self.is_trivial_mode:
            self.current_chain = self.trivial_converse
        else:
            self.current_chain = self.story_converse
        
        # Record the model order in the user's data directory
        with open(f'data/{session_id}/model_order.txt', 'w') as f:
            f.write(f'{'A/B' if self.is_trivial_mode else 'B/A'}')

        await ctx.reply("Experiment started!")

    @commands.hybrid_command(name="second_mode")
    async def second_mode(self, ctx: commands.Context[commands.Bot]):
        """Switch to the other experimental mode"""

        with open(f'data/{ctx.author.name}/model_order.txt', 'r') as f:
            order = f.read()

        if order == 'A/B':
            self.current_chain = self.story_converse
        else:
            self.current_chain = self.trivial_converse
            
        await ctx.reply("Mode switched!")



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
        #print('Event triggered! Message content:', message.content)

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

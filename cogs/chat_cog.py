import random
import os
import logging
import discord
from discord.ext import commands

# Trivial system
from generator.trivial import get_chain as get_trivial_chain
# Our system
from generator.story import get_chain as get_story_chain

logger = logging.getLogger(__name__)
first_message = """
Tu te trouves au cœur de ce qui était autrefois une ville prospère, aujourd'hui réduite à un chaos silencieux appelé Ville Fantôme. Autour de toi, les bâtiments délabrés témoignent d’une époque passée tandis que les ombres mouvantes des zombies hantent chaque coin sombre. Tu es Alexandre Durand, un ingénieur civil transformé en survivant aguerri depuis le début de cette pandémie terrifiante. Ta conviction reste intacte : trouver un moyen de stopper définitivement ces créatures infectées est non seulement ta mission personnelle, mais aussi celle de tous ceux qui espèrent voir renaître une forme quelconque de normalité. La route sera longue et périlleuse, mais tu sais désormais que chaque détail peut faire la différence entre la survie et l’extinction. Que décides-tu de faire ?
"""


class ChatCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.started = False
        self.setting = "Post-apocalypse zombie mondiale, 1 an après le début de l'épidémie"
        self.language = "french"
        self.first_message = first_message
        #self.invoke_current_chain = None

        self.invoke_current_chain = get_story_chain(
            self.bot.model,
            self.bot.predictable_model,
            self.first_message, 
            self.setting, 
            self.language,
            'foo', 
            {"configurable": {"session_id": 'foo'}}
        )

    
    # Define a command to choose between trivial and story mode
    @commands.hybrid_command(name="set_mode")
    async def set_mode(self, ctx: commands.Context[commands.Bot], mode: str, session_id: str):
        await ctx.defer()  # Acknowledge the command to prevent timeout
        try:
            if mode == "trivial":
                self.invoke_current_chain = get_trivial_chain(
                    self.bot.model, 
                    self.first_message, 
                    self.setting, 
                    self.language, 
                    session_id, 
                    {"configurable": {"session_id": session_id}}
                )
            elif mode == "story":
                self.invoke_current_chain = get_story_chain(
                    self.bot.model,
                    self.bot.predictable_model,
                    self.first_message, 
                    self.setting, 
                    self.language, 
                    session_id, 
                    {"configurable": {"session_id": session_id}}
                )
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
            self.invoke_current_chain = get_trivial_chain(
                self.bot.model, 
                self.first_message, 
                self.setting, 
                self.language, 
                session_id, 
                {"configurable": {"session_id": session_id}}
            )
        else:
            self.invoke_current_chain = get_story_chain(
                self.bot.model, 
                self.first_message, 
                self.setting, 
                self.language, 
                session_id, 
                {"configurable": {"session_id": session_id}}
            )
        
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
            self.invoke_current_chain = get_story_chain(self.bot.model, self.first_message, ctx.author.name)
        else:
            self.invoke_current_chain = get_trivial_chain(self.bot.model, self.first_message)
            
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
        if self.invoke_current_chain is None:
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
            response = await self.invoke_current_chain(message.content)

        # Send the LLM response in the channel
        await message.channel.send(response)


async def setup(bot: commands.Bot):
    await bot.add_cog(ChatCog(bot))


async def teardown(bot: commands.Bot):
    # print(f"{__name__} unloaded!")
    pass

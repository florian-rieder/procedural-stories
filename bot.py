"""
Based on https://fallendeity.github.io/discord.py-masterclass
Mostly boilerplate code.
We load the LLM here to only load it once.
"""

import asyncio
import certifi
import configparser
import datetime
import importlib
import logging
import os
import sys
import time
import traceback
import typing

import discord
from discord.ext import commands
from dotenv import load_dotenv

from generator.models import model


# Fix SSL error: https://stackoverflow.com/a/78935128/10914628
os.environ["SSL_CERT_FILE"] = certifi.where()

CONFIG_FILE = "config.ini"


# Doesn't work
def reload_module_by_path(file_path):
    # Check if the module is already loaded
    for module_name, module in sys.modules.items():
        if getattr(module, "__file__", None) == file_path:
            # If found, reload it and return the reloaded module
            return importlib.reload(module)

    # module_name = file_path[:-3].replace("/", ".")

    # # If the module is not yet loaded, import it
    # spec = importlib.util.spec_from_file_location(module_name, file_path)
    # module = importlib.util.module_from_spec(spec)
    # sys.modules[spec.name] = module
    # spec.loader.exec_module(module)
    return module


class StorytellerBot(commands.Bot):
    config: configparser.ConfigParser = configparser.ConfigParser()
    _uptime: datetime.datetime = datetime.datetime.now()
    _watcher: asyncio.Task

    def __init__(
        self, prefix: str, ext_dir: str, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        # Declare intents
        # see https://discordpy.readthedocs.io/en/stable/api.html#intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.messages = True

        super().__init__(
            *args,
            **kwargs,
            command_prefix=commands.when_mentioned_or(prefix),
            intents=intents,
        )
        self.logger = logging.getLogger(self.__class__.__name__)
        self.ext_dir = ext_dir
        self.synced = False

    async def _load_extensions(self) -> None:
        if not os.path.isdir(self.ext_dir):
            self.logger.error(f"Extension directory {self.ext_dir} does not exist.")
            return
        for filename in os.listdir(self.ext_dir):
            if filename.endswith(".py") and not filename.startswith("_"):
                try:
                    await self.load_extension(f"{self.ext_dir}.{filename[:-3]}")
                    self.logger.info(f"Loaded extension {filename[:-3]}")
                except commands.ExtensionError:
                    self.logger.error(
                        f"Failed to load extension {filename[:-3]}\n{traceback.format_exc()}"
                    )
        await self.tree.sync()

    async def on_error(
        self, event_method: str, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        self.logger.error(
            f"An error occurred in {event_method}.\n{traceback.format_exc()}"
        )

    async def on_ready(self) -> None:
        self.logger.info(f"Logged in as {self.user} ({self.user.id})")

    async def setup_hook(self) -> None:
        # # Load config
        # if os.path.isfile(CONFIG_FILE):
        #     # Read config
        #     self.config.read(CONFIG_FILE)
        # else:
        #     # If there is no config file, write default config
        #     self.config['DEFAULT']['SPREADSHEET_FILENAME'] = os.getenv('DEFAULT_SPREADSHEET_NAME', 'default')
        #     self.config['DEFAULT']['MESSAGES_LIMIT'] = '100'
        #     self.save_config()

        ########################################################################
        #                            Initialize LLM                            #
        ########################################################################

        # Load LLM
        self.model = model

        ########################################################################
        #                    Load extensions and watch files                   #
        ########################################################################

        # Load cogs
        await self._load_extensions()

        # Initialize cog watcher
        self._watcher = self.loop.create_task(self._cog_watcher())

        # Sync with discord
        if not self.synced:
            await self.tree.sync()
            self.synced = not self.synced
            self.logger.info("Synced command tree")

    # def save_config(self):
    #     with open(CONFIG_FILE, 'w') as configfile:
    #         self.config.write(configfile)

    async def close(self) -> None:
        await super().close()

    async def _cog_watcher(self):
        print("Watching for changes...")
        last = time.time()

        while True:
            extensions: set[str] = set()
            files_to_watch = []  # List of files to check for changes

            # Check extensions for changes
            for name, module in self.extensions.items():
                if module.__file__ and os.stat(module.__file__).st_mtime > last:
                    extensions.add(name)

            # Add story.py to files to watch
            story_file = "story.py"
            if os.path.isfile(story_file) and os.stat(story_file).st_mtime > last:
                files_to_watch.append(story_file)

            # Add all Python files in the 'generator' directory to files to watch
            generator_dir = "generator"
            if os.path.isdir(generator_dir):
                for filename in os.listdir(generator_dir):
                    if filename.endswith(".py"):
                        file_path = os.path.join(generator_dir, filename)
                        if os.stat(file_path).st_mtime > last:
                            files_to_watch.append(file_path)

            # Reload extensions that have changed
            for ext in extensions:
                try:
                    await self.reload_extension(ext)
                    print(f"Reloaded {ext}")
                except commands.ExtensionError as e:
                    print(f"Failed to reload {ext}: {e}")

            # Reload or refresh files like story.py and generator files if they change
            if files_to_watch:
                for file in files_to_watch:
                    print(f"Detected change in {file}, reloading relevant components.")
                    reload_module_by_path(file)

            last = time.time()
            await asyncio.sleep(1)

    def run(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        load_dotenv()
        try:
            super().run(str(os.getenv("DISCORD_TOKEN")), *args, **kwargs)
        except (discord.LoginFailure, KeyboardInterrupt):
            self.logger.info("Exiting...")
            exit()

    @property
    def user(self) -> discord.ClientUser:
        assert super().user, "Bot is not ready yet"
        return typing.cast(discord.ClientUser, super().user)

    @property
    def uptime(self) -> datetime.timedelta:
        return datetime.datetime.now() - self._uptime


def main() -> None:
    logging.basicConfig(
        level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s"
    )
    bot = StorytellerBot(prefix="!", ext_dir="cogs")
    bot.run()


if __name__ == "__main__":
    main()
    # mod = reload_module_by_path('generator/trivial.py')
    # print(mod.get_chain)

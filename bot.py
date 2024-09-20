"""
Based on https://fallendeity.github.io/discord.py-masterclass
"""

import asyncio
import configparser
import datetime
import logging
import os
import time
import traceback
import typing

import discord
from discord.ext import commands
from dotenv import load_dotenv

from story import get_chain

import certifi


# Fix SSL error: https://stackoverflow.com/a/78935128/10914628
os.environ["SSL_CERT_FILE"] = certifi.where()

CONFIG_FILE = 'config.ini'

class StorytellerBot(commands.Bot):
    config: configparser.ConfigParser = configparser.ConfigParser()
    _uptime: datetime.datetime = datetime.datetime.now()
    _watcher: asyncio.Task

    def __init__(self, prefix: str, ext_dir: str, *args: typing.Any, **kwargs: typing.Any) -> None:
        # Declare intents
        # see https://discordpy.readthedocs.io/en/stable/api.html#intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.messages = True
        super().__init__(*args, **kwargs,
                         command_prefix=commands.when_mentioned_or(prefix), intents=intents)
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
                    self.logger.error(f"Failed to load extension {filename[:-3]}\n{traceback.format_exc()}")
        await self.tree.sync()

    async def on_error(self, event_method: str, *args: typing.Any, **kwargs: typing.Any) -> None:
        self.logger.error(f"An error occurred in {event_method}.\n{traceback.format_exc()}")

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

        # Initialize LLM pipeline
        self.chain = get_chain()

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
            for name, module in self.extensions.items():
                if module.__file__ and os.stat(module.__file__).st_mtime > last:
                    extensions.add(name)
            for ext in extensions:
                try:
                    await self.reload_extension(ext)
                    print(f"Reloaded {ext}")
                except commands.ExtensionError as e:
                    print(f"Failed to reload {ext}: {e}")
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
    logging.basicConfig(level=logging.INFO,
                        format="[%(asctime)s] %(levelname)s: %(message)s")
    bot = StorytellerBot(prefix="!", ext_dir="cogs")
    bot.run()


if __name__ == "__main__":
    main()

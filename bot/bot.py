"""MAGPB: MrArkon's General Purpose Bot
Copyright (C) 2023 MrArkon

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>."""
import datetime
from logging import getLogger

import discord
from discord.ext import commands, tasks
from jishaku.modules import find_extensions_in

from bot import __version__, config

__log__ = getLogger(__name__)


class Bot(commands.Bot):
    """Represents the main bot instance, subclasses :class:`commands.Bot`
    for utility methods shared between plugins."""

    launched_at: datetime.datetime

    def __init__(self) -> None:
        intents = discord.Intents(guilds=True, guild_messages=True)
        allowed_mentions = discord.AllowedMentions(everyone=False, users=True, roles=False, replied_user=False)
        activity = discord.Activity(name="myself boot up", type=discord.ActivityType.watching)

        super().__init__(
            command_prefix=commands.when_mentioned,
            intents=intents,
            allowed_mentions=allowed_mentions,
            activity=activity,
            owner_ids=config.OWNER_IDS,
            help_command=None,
            max_messages=None,
            heartbeat_timeout=90.0,
        )

    async def setup_hook(self) -> None:
        plugins = find_extensions_in("bot/plugins")

        failed = 0
        for plugin in plugins:
            try:
                await self.load_extension(plugin)
            except Exception as exc:
                failed += 1
                __log__.error(f"Failed to load plugin '{plugin}'", exc_info=exc)

        total = len(list(self.walk_commands())) + len(list(self.tree.walk_commands()))
        message = f"Loaded {len(plugins) - failed} plugins with {total} commands"
        if failed:
            message += f" | Failed to load {failed} plugins"

        __log__.info(message)

        self.update_activity.start()

    @tasks.loop(minutes=10.0)
    async def update_activity(self) -> None:
        await self.wait_until_ready()

        activity = discord.Activity(name=f"/help | {len(self.guilds)} servers", type=discord.ActivityType.watching)
        await self.change_presence(activity=activity)

    async def on_ready(self) -> None:
        prefix = "Reconnected"

        if not hasattr(self, "launched_at"):
            prefix = "Logged in"
            self.launched_at = discord.utils.utcnow()

        if self.user is not None:
            __log__.info(f"{prefix} as {self.user} [ID: {self.user.id}] | Running MAGPB v{__version__}")

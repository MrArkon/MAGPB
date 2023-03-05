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
import asyncio
import os
from contextlib import suppress
from logging import getLogger

import discord

from bot import Bot, config

os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"


async def main() -> None:
    discord.utils.setup_logging()

    for name, value in config.LOGGING.items():
        getLogger(name).setLevel(value)

    discord.VoiceClient.warn_nacl = False

    async with Bot() as bot:
        await bot.start(config.TOKEN)


if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        asyncio.run(main())

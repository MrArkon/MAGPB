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
from __future__ import annotations

from typing import TYPE_CHECKING

from discord.ext import commands

if TYPE_CHECKING:
    from bot import Bot

__all__ = ("Plugin",)


class Plugin(commands.Cog):
    """Represents the base cog class. Implements the default :meth:`__init__`
    to assign the bot attribute.

    Attributes
    ----------
    bot: :class:`Bot`
        The main bot instance.
    """

    __slots__ = "bot"

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

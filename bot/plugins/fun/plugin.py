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
from discord.ext import commands

from bot import models

from .views import Minesweeper


class Fun(models.Plugin):
    @commands.command(aliases=["ms"])
    async def minesweeper(self, ctx: models.Context) -> None:
        """Can you find all the mines in minimum possible time and moves?"""
        view = Minesweeper(ctx, 4)
        view.message = await ctx.reply(embed=view.build_embed(), view=view)
        await view.wait()

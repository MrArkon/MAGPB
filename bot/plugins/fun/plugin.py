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
import discord
from discord import app_commands as app

from bot import models

from .views import Minesweeper


class Fun(models.Plugin):
    @app.command()
    @app.describe(mines="The amount of mines to place.")
    async def minesweeper(self, interaction: discord.Interaction, mines: app.Range[int, 3, 24] = 4) -> None:
        """Can you find all the mines in minimum possible time and moves?"""
        view = Minesweeper(interaction, mines)
        await interaction.response.send_message(embed=view.build_embed(), view=view)
        view.message = await interaction.original_response()

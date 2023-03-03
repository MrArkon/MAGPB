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
from contextlib import suppress
from typing import TYPE_CHECKING

import discord
from discord import app_commands as app

if TYPE_CHECKING:
    from bot import Bot


class CommandTree(app.CommandTree):
    """Represents the command tree, subclasses :class:`app_commands.CommandTree`
    for applying global checks and handling errors
    """

    client: Bot

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.guild is not None

    async def on_error(self, interaction: discord.Interaction, error: app.AppCommandError) -> None:
        send = interaction.followup.send if interaction.response.is_done() else interaction.response.send_message
        error = getattr(error, "original", error)

        # Unknown Error
        embed = discord.Embed(color=discord.Color.red())
        embed.description = (
            "Something went wrong while trying to process your request. I have notified my developers. "
            f"\n\n```python\n{error.__class__.__name__}: {error}```"
        )

        embed.set_author(name=str(interaction.user), icon_url=interaction.user.display_avatar.url)

        with suppress(discord.HTTPException, discord.Forbidden):
            await send(embed=embed)

        await super().on_error(interaction, error)

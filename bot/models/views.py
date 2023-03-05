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

import discord

from bot import config


class View(discord.ui.View):
    """Represents the base UI View, implements the basic boilerplate
    and adds various helper methods to the default :class:`discord.ui.View`

    Parameters
    ----------
    interaction: :class:`discord.Interaction`
        The app command interaction.
    timeout: :class:`float` | ``None``
        The timeout in seconds from last interaction with the UI before
        no longer accepting input. defaults to 180, If ``None`` then there
        is no timeout.
    on_complete: :class:`bool` | ``None``
        A tribool that indicated what happens when the View completes,
        ``True`` disabled all children, ``False`` deletes the message containing
        this View and ``None`` does nothing.
    """

    def __init__(self, interaction: discord.Interaction, *, timeout: float | None = 180, on_complete: bool | None = True):
        self.interaction = interaction
        self.on_complete = on_complete

        super().__init__(timeout=timeout)

        self.message: discord.Message | None = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """A callback that is called when an interaction happens within the view
        that checks whether the view should process item callbacks for the interaction.

        The default implementation of this returns whether the user is the author of
        the app command which invokes this View.

        Returns
        -------
        :class:`bool`
        """
        return interaction.user == self.interaction.user

    async def on_error(self, interaction: discord.Interaction, error: Exception, item: discord.ui.Item) -> None:
        """A callback that is called when an item's callback or :meth:`interaction_check`
        raises an error. This implementation notifies the user and logs to the logger.
        """
        send = interaction.followup.send if interaction.response.is_done() else interaction.response.send_message

        embed = discord.Embed(
            description="Something went wrong while trying to process your request. I have notified my developers. "
            f"\n\n```python\n{error.__class__.__name__}: {error}```",
            color=config.RED,
        )

        embed.set_author(name=str(interaction.user), icon_url=interaction.user.display_avatar.url)

        with suppress(discord.HTTPException, discord.Forbidden):
            await send(embed=embed)

        await super().on_error(interaction, error, item)

    async def cleanup(self) -> None:
        """A callback for cleaning up the View on the basis of the
        :attr:`on_complete` attribute.
        """
        if self.message is not None:
            with suppress(discord.NotFound, discord.HTTPException):
                # disable children
                if self.on_complete is True:
                    for item in self.children:
                        if isinstance(item, (discord.ui.Button, discord.ui.Select)):
                            item.disabled = True

                    await self.message.edit(view=self)
                # delete message
                elif self.on_complete is False:
                    await self.message.delete()

        self.stop()

    async def on_timeout(self) -> None:
        await self.cleanup()

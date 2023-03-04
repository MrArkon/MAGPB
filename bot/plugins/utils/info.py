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

from bot import config, models


class Information(models.Plugin):
    info = app.Group(name="info", description="The parent command for informational commands.")

    @info.command()
    @app.describe(user="The user you want information about, defaults to you if not provided.")
    async def user(self, interaction: discord.Interaction, user: discord.Member | discord.User | None = None) -> None:
        """Obtain information about any user, whether in the server or not."""
        user = user or interaction.user

        embed = discord.Embed(colour=config.BLUE if user.colour == discord.Colour.default() else user.colour)
        embed.title = f"{user} " + " ".join(str(config.BADGES.get(name, "")) for name, value in user.public_flags if value)

        embed.set_thumbnail(url=user.display_avatar)
        embed.set_footer(text=f"ID: {user.id}")

        embed.add_field(
            name="Discord User Since", value="\n".join(discord.utils.format_dt(user.created_at, style=f) for f in ("D", "R"))
        )

        if isinstance(user, discord.Member):
            assert interaction.guild is not None

            if user.joined_at is not None:
                embed.add_field(
                    name="Server Member Since",
                    value="\n".join(discord.utils.format_dt(user.joined_at, style=f) for f in ("D", "R")),
                )

            sorted_members = sorted(interaction.guild.members, key=lambda member: member.joined_at or discord.utils.utcnow())
            embed.add_field(name="Join Position", value=f"{sorted_members.index(user) + 1:,}/{len(sorted_members):,}")

            embed.add_field(
                name=f"Roles [{len(user.roles)}]:",
                value=", ".join(
                    role.mention if not role.is_default() else "@everyone"
                    for role in sorted(user.roles, key=lambda role: role.position, reverse=True)
                ),
            )

            embed.add_field(
                name="Key Permissions",
                value=(
                    ", ".join(
                        f"{permission.replace('_', ' ').title()}"
                        for permission, value in user.guild_permissions & discord.Permissions(27812569150)
                        if value
                    )
                    if not user.guild_permissions.administrator
                    else "Administrator"
                )
                or "None",
            )

        view = discord.ui.View(timeout=None)

        view.add_item(discord.ui.Button(label="View Avatar", style=discord.ButtonStyle.link, url=user.display_avatar.url))

        view.add_item(
            discord.ui.Button(
                label="View Profile", style=discord.ButtonStyle.link, url=f"https://discord.com/users/{user.id}"
            )
        )

        if isinstance(user, discord.Member):
            view.add_item(
                discord.ui.Button(
                    label="View All Permissions",
                    style=discord.ButtonStyle.link,
                    url=f"https://discordapi.com/permissions.html#{user.guild_permissions.value}",
                )
            )

        await interaction.response.send_message(embed=embed, view=view)

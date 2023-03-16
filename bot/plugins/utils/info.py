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
from discord.ext import commands

from bot import config, models


class Information(models.Plugin):
    @commands.command(aliases=["memberinfo", "mi", "ui", "whois"])
    async def userinfo(self, ctx: models.Context, user: discord.Member | discord.User | None = None) -> None:
        """Obtain information about any user, whether in the server or not."""
        user = user or ctx.author

        embed = discord.Embed(colour=config.BLUE if user.colour == discord.Colour.default() else user.colour)
        embed.title = f"{user} " + " ".join(str(config.BADGES.get(name, "")) for name, value in user.public_flags if value)

        embed.set_thumbnail(url=user.display_avatar)
        embed.set_footer(text=f"ID: {user.id}")

        general = [
            f"Discord User Since: {discord.utils.format_dt(user.created_at, style='D')} "
            f"({discord.utils.format_dt(user.created_at, style='R')})"
        ]

        if isinstance(user, discord.Member):
            if user.joined_at is not None:
                general.append(
                    f"Server Member Since: {discord.utils.format_dt(user.joined_at, style='D')} "
                    f"({discord.utils.format_dt(user.joined_at, style='R')})"
                )

            sorted_members = sorted(ctx.guild.members, key=lambda member: member.joined_at or discord.utils.utcnow())
            general.append(f"Join Position: {sorted_members.index(user) + 1:,}/{len(sorted_members):,}")

        embed.add_field(name="General", value="\n".join(general), inline=False)

        if isinstance(user, discord.Member):
            embed.add_field(
                name=f"Roles [{len(user.roles)}]",
                value=" ".join(
                    role.mention if not role.is_default() else "@everyone"
                    for role in sorted(user.roles, key=lambda role: role.position, reverse=True)[:10]
                ),
                inline=False,
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
                inline=False,
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

        await ctx.reply(embed=embed, view=view)

    @commands.command(aliases=["si"])
    async def serverinfo(self, ctx: models.Context) -> None:
        """Obtain information about this server."""
        guild = ctx.guild

        embed = discord.Embed(title=guild.name, color=config.BLUE)
        embed.set_thumbnail(url=getattr(guild.icon, "url", None))

        general = [
            f"Owned By: {guild.owner.mention if guild.owner else 'N/A'}",
            f"Created At: {discord.utils.format_dt(guild.created_at, 'D')} "
            f"({discord.utils.format_dt(guild.created_at, 'R')})",
        ]

        embed.add_field(name="General", value="\n".join(general), inline=False)

        mfa_level = "Yes" if guild.mfa_level is discord.MFALevel.require_2fa else "No"

        if guild.explicit_content_filter is discord.ContentFilter.disabled:
            content_filter = "Disabled"
        elif guild.explicit_content_filter is discord.ContentFilter.no_role:
            content_filter = "Enabled for members without roles"
        else:
            content_filter = "Enabled for everyone"

        moderation = [
            f"Require 2FA for moderator actions: {mfa_level}",
            f"Explicit Media Content Filter: {content_filter}",
            f"Verification Level: {str(guild.verification_level).capitalize()}",
        ]

        embed.add_field(name="Moderation", value="\n".join(moderation), inline=False)

        bots = sum(member.bot for member in guild.members)
        integrated = sum(r.is_integration() for r in guild.roles)

        counts = [
            f"Members: {guild.member_count:,}{f' ({bots} bots)' if bots else ''} " f"/ {guild.max_members:,}",
            f"Roles: {len(guild.roles)}{f' ({integrated} integrated)' if integrated else ''} / 250",
            f"Stickers: {len(guild.stickers)} / {guild.sticker_limit}",
            f"Emojis: {sum(not e.animated for e in guild.emojis)} / {guild.emoji_limit} static"
            f"; {sum(e.animated for e in guild.emojis)} / {guild.emoji_limit} animated",
        ]

        text, locked_text = 0, 0
        voice, locked_voice = 0, 0
        total = 0

        for channel in guild.channels:
            allowed, denied = channel.overwrites_for(guild.default_role).pair()
            permissions = discord.Permissions((guild.default_role.permissions.value & ~denied.value) | allowed.value)

            if isinstance(channel, (discord.TextChannel, discord.ForumChannel)):
                text += 1
                if not permissions.read_messages:
                    locked_text += 1
            elif isinstance(channel, (discord.VoiceChannel, discord.StageChannel)):
                voice += 1
                if not permissions.connect:
                    locked_voice += 1

            total += 1

        counts.append(
            f"Channels: {text} text{f' ({locked_text} locked)' if locked_text else ''} "
            f"and {voice} voice{f' ({locked_voice} locked)' if locked_voice else ''} "
            f"- {total} / 500"
        )

        embed.add_field(name="Counts", value="\n".join(counts), inline=False)

        premium = [
            f"Level {guild.premium_tier} ({guild.premium_subscription_count} Boosts)",
            f"Boosters: {len(guild.premium_subscribers)}",
        ]

        last_boost = max(guild.members, key=lambda m: m.premium_since or guild.created_at)  # type: ignore
        if last_boost.premium_since is not None:
            premium.append(f"Last Booster: {last_boost.mention} ({discord.utils.format_dt(last_boost.premium_since, 'R')})")

        embed.add_field(name="Premium", value="\n".join(premium), inline=False)

        embed.set_footer(text=f"ID: {guild.id}")

        await ctx.reply(embed=embed)

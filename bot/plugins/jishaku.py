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
from platform import python_version, release, system

import discord
import psutil
from discord.ext import commands
from jishaku.cog import OPTIONAL_FEATURES, STANDARD_FEATURES
from jishaku.features.baseclass import Feature
from jishaku.math import natural_size
from jishaku.modules import package_version

from bot import Bot, models


class Jishaku(*OPTIONAL_FEATURES, *STANDARD_FEATURES):
    @Feature.Command(name="jishaku", aliases=["jsk"], invoke_without_command=True)
    async def jsk(self, ctx: models.Context) -> None:
        description = [
            f"Jishaku v{package_version('jishaku')}, discord.py v{discord.__version__}, "
            f"Python v{python_version()} on {system()} {release()}",
            f"Module was loaded {discord.utils.format_dt(self.load_time, 'R')}, "
            f"cog was loaded {discord.utils.format_dt(self.start_time, 'R')}\n",
        ]

        try:
            proc = psutil.Process()

            with proc.oneshot():
                with suppress(psutil.AccessDenied):
                    mem = proc.memory_full_info()
                    description.append(
                        f"Using {natural_size(mem.rss)} physical memory and "
                        f"{natural_size(mem.vms)} virtual memory, "
                        f"{natural_size(mem.uss)} of which unique to this process."
                    )

                with suppress(psutil.AccessDenied):
                    name = proc.name()
                    pid = proc.pid
                    thread_count = proc.num_threads()
                    util = proc.cpu_percent() / psutil.cpu_count()

                    description.append(
                        f"Running on PID {pid} (`{name}`) with {util}% CPU utilization "
                        f"on {psutil.cpu_count()} cores and {thread_count} thread(s)."
                    )
        except psutil.AccessDenied:
            description.append("This process does not have high enough access rights to query process information.")

        description.append("")

        s_for_guilds = "" if len(self.bot.guilds) == 1 else "s"
        s_for_users = "" if len(self.bot.users) == 1 else "s"
        cache_description = f"{len(self.bot.guilds)} guild{s_for_guilds} and {len(self.bot.users)} user{s_for_users}"

        # Show shard settings to summary
        if isinstance(self.bot, discord.AutoShardedClient):
            if len(self.bot.shards) > 20:
                description.append(
                    f"This bot is automatically sharded ({len(self.bot.shards)} shards of {self.bot.shard_count})"
                    f" and can see {cache_description}."
                )
            else:
                shard_ids = ", ".join(str(i) for i in self.bot.shards.keys())
                description.append(
                    f"This bot is automatically sharded (Shards {shard_ids} of {self.bot.shard_count})"
                    f" and can see {cache_description}."
                )
        elif self.bot.shard_count:
            description.append(
                f"This bot is manually sharded (Shard {self.bot.shard_id} of {self.bot.shard_count})"
                f" and can see {cache_description}."
            )
        else:
            description.append(f"This bot is not sharded and can see {cache_description}.")

        remarks = {True: "enabled", False: "disabled", None: "unknown"}

        *group, last = (
            f"{intent.replace('_', ' ')} intent is {remarks.get(getattr(self.bot.intents, intent, None))}"
            for intent in ("presences", "members", "message_content")
        )

        if self.bot._connection.max_messages:
            message_cache = f"Message cache capped at {self.bot._connection.max_messages}"
        else:
            message_cache = "Message cache is disabled"

        description.append(f"{message_cache}, {', '.join(group)}, and {last}.")

        embed = discord.Embed(description="\n".join(description), colour=0x302C34)
        embed.set_footer(text=f"Average websocket latency: {self.bot.latency * 1000:0.2f}ms")
        await ctx.send(embed=embed)


async def setup(bot: Bot) -> None:
    await bot.add_cog(Jishaku(bot=bot))

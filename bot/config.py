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
import tomllib

from discord import Colour, PartialEmoji

with open("config.toml", "rb") as f:
    f = tomllib.load(f)

TOKEN = f["bot"]["token"]
OWNER_IDS = f["bot"]["owner_ids"]

BLUE = Colour.from_str(f["colors"]["blue"])
RED = Colour.from_str(f["colors"]["red"])

BADGES: dict[str, PartialEmoji] = {}
for name, id in f["badges"].items():
    BADGES[name] = PartialEmoji(name=name, id=id)

LOGGING: dict[str, int] = f["logging"]

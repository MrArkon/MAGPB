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


def readable(seconds: int | float, decimal: bool = False, short: bool = False) -> str:
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)
    months, days = divmod(days, 30)  # Approximately
    years, months = divmod(months, 12)

    attrs = {
        "y" if short else "year": years,
        "mo" if short else "month": months,
        "d" if short else "day": days,
        "hr" if short else "hour": hours,
        "m" if short else "minute": minutes,
        "s" if short else "second": seconds,
    }

    output = []
    for unit, value in attrs.items():
        value = round(value, 2 if decimal else None)
        if value > 0:
            output.append(f"{value}{' ' * (not short)}{unit}{('s' if value != 1 else '') * (not short)}")

    return ", ".join(output)


def timestamp(seconds: int | float) -> str:
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    _, hours = divmod(hours, 24)

    return f"{hours:0>2.0f}:{minutes:0>2.0f}:{seconds:0>2.0f}" if hours else f"{minutes:0>2.0f}:{seconds:0>2.0f}"

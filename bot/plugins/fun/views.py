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
from random import randint
from time import perf_counter

import discord

from bot import config, models
from bot.utilities import readable

deltas: list[tuple[int, int]] = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]


class Cell:
    def __init__(self) -> None:
        self.value = 0  # The displayed value on the board, -1 represents a mine.
        self.selected = False


class Minesweeper(models.View):
    def __init__(self, interaction: discord.Interaction, mines: int):
        super().__init__(interaction, timeout=90)

        self.mines = mines
        self.moves: int = 0
        self.start = perf_counter()

        # Generate Board
        self.board = [[Cell() for _ in range(5)] for _ in range(5)]
        self.place_mines()

        for x in range(5):
            for y in range(5):
                self.add_item(MinesweeperButton(self.board[x][y], (x, y)))

    async def terminate(
        self, interaction: discord.Interaction | None = None, won: bool = False, *, position: tuple[int, int] | None = None
    ) -> None:
        if self.message is None and interaction is None:
            return

        duration = perf_counter() - self.start

        for item in self.children:
            if isinstance(item, MinesweeperButton):
                item.disabled = True

                if item.cell.value == -1:
                    if item.position == position:
                        item.label = "\N{COLLISION SYMBOL}"
                    else:
                        item.label = "\N{TRIANGULAR FLAG ON POST}" if won else "\N{BOMB}"
                    item.style = discord.ButtonStyle.green if won else discord.ButtonStyle.red
                else:
                    item.style = discord.ButtonStyle.gray
                    item.label = str(item.cell.value) if item.cell.value != 0 else "‎"

        embed = discord.Embed(
            description=f"{self.interaction.user.mention} {'found all' if won else 'exploded by'}"
            f" {self.mines} mines in {self.moves} moves | Time: {readable(duration, short=True)}",
            colour=config.BLUE if won else config.RED,
        )

        with suppress(discord.NotFound, discord.HTTPException):
            if interaction:
                await interaction.response.edit_message(embed=embed, view=self)
            elif self.message:
                await self.message.edit(embed=embed, view=self)

        self.stop()

    def build_embed(self) -> discord.Embed:
        return discord.Embed(
            description=f"{self.interaction.user.mention}'s Minesweeper Game | Moves: {self.moves} | Mines: {self.mines}",
            colour=config.BLUE,
        )
        
    def place_mines(self) -> None:
        previous = set()
        for _ in range(self.mines):
            x, y = randint(0, 4), randint(0, 4)

            while (x, y) in previous:
                x, y = randint(0, 4), randint(0, 4)

            self.board[y][x].value = -1

            for j, i in self.get_neighbours(y, x):
                if self.board[j][i].value != -1:
                    self.board[j][i].value += 1

            previous.add((x, y))

    def get_neighbours(self, x: int, y: int) -> list[tuple[int, int]]:
        return [(x + i, y + j) for i, j in deltas if (0 <= x + i and x + i < 5) and (0 <= y + j and y + j < 5)]

    def mark(self, x: int, y: int) -> bool:
        self.board[x][y].selected = True

        if self.board[x][y].value == -1:
            return False
        elif self.board[x][y].value == 0:
            for i, j in self.get_neighbours(x, y):
                if not self.board[i][j].selected:
                    self.mark(i, j)

        return True


class MinesweeperButton(discord.ui.Button["Minesweeper"]):
    def __init__(self, cell: Cell, position: tuple[int, int]):
        self.position = position
        self.cell = cell

        super().__init__()
        self._update_labels()

    def _update_labels(self) -> None:
        if self.view is not None:
            self.cell = self.view.board[self.position[0]][self.position[1]]

        if self.cell.selected:
            self.style = discord.ButtonStyle.secondary
            self.label = str(self.cell.value) if self.cell.value != 0 else "‎"
        else:
            self.label = "‎"
            self.style = discord.ButtonStyle.blurple

        self.disabled = self.cell.selected

    async def callback(self, interaction: discord.Interaction) -> None:
        assert self.view is not None

        self.view.moves += 1
        self.cell = self.view.board[self.position[0]][self.position[1]]

        if not self.view.mark(*self.position):
            return await self.view.terminate(interaction, position=self.position)

        if self.cell.value == 0:
            for button in self.view.children:
                if isinstance(button, MinesweeperButton):
                    if not button.disabled:
                        button._update_labels()
        else:
            self._update_labels()

        if all(all(cell.selected for cell in row if cell.value != -1) for row in self.view.board):
            return await self.view.terminate(interaction, True)

        await interaction.response.edit_message(embed=self.view.build_embed(), view=self.view)

"""
If there are 81 groups of digits, the data is interpreted as a candidate grid.
All formatting is ignored.

If there are N digits and 81-N occurrences of another character, this character
will be interpreted as representing an empty cell. When multiple characters add
up to 81, the following preference list is used: '0', '.', 'X', '*', '_', ' '
"""

from typing import TYPE_CHECKING

from .interface import AbsSudokuWriter

if TYPE_CHECKING:
    from typing import TextIO

    from sudoku_strategy.grid import Grid


class SusserWriter(AbsSudokuWriter):
    def write(self, grid: Grid, stream: TextIO):
        """Write a susser format from a text stream"""
        for cell in grid.analyse.cell_groups.cells():
            digit = grid.analyse.get_digit_in_cell(cell)

            if digit == 0:
                stream.write(".")
            else:
                stream.write(str(digit))

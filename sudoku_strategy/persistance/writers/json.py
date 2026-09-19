"""
A json object containing three fields:
    * puzzle_digits: A list of 81 numbers representing the puzzles initial
        starting numbers. 0 is used to represent an empty cell.
    * digits: A list of 81 numbers representing the digits filled in the grid.
        This includes the digits set in puzzle_digits uses 0 to represent an
        empty cell.
    * candidate_values: A list of 81 lists. Each sub list can contain the
        numbers 1-9 representing the candidates for the relevant cell.

Example of the json format:

{
  "puzzle_digits": [0, 0, 3, 0, ...],
  "digits": [1, 0, 3, 0, ...],
  "candidate_values": [
    [],
    [7, 8, 9],
    [],
    ...
  ]
}
"""

import json
from typing import TYPE_CHECKING

from .interface import AbsSudokuWriter

if TYPE_CHECKING:
    from typing import TextIO

    from sudoku_strategy.grid import Grid


class JsonWriter(AbsSudokuWriter):
    def write(self, grid: Grid, stream: TextIO):
        """Read a json format from a text stream."""
        grid_dict = {
            "puzzle_digits": [],
            "digits": [],
            "candidate_values": [],
        }

        for cell in grid.analyse.cell_groups.cells():
            digit = grid.analyse.get_digit_in_cell(cell)
            puzzle_digit = grid.analyse.is_puzzle_digit(cell) and digit or 0
            candidates = grid.analyse.get_candidates_for_cell(cell)

            grid_dict["puzzle_digits"].append(puzzle_digit)
            grid_dict["digits"].append(digit)
            grid_dict["candidate_values"].append(list(candidates))

        json.dump(grid_dict, stream)

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

from sudoku_strategy.grid import Cell, Grid

from .interface import AbsSudokuReader

if TYPE_CHECKING:
    from typing import TextIO


class JsonReader(AbsSudokuReader):
    def read(self, stream: TextIO) -> Grid:
        """Read a json format from a text stream."""
        grid_dict = json.load(stream)

        # Create grid with the given puzzle digits
        grid = Grid.new_puzzle(tuple(grid_dict["puzzle_digits"]))

        # Add the entered digits to the grid
        for idx, val in enumerate(grid_dict["digits"]):
            if val != 0:
                cell = Cell(idx)
                grid.modify.write_digit(val, cell)

        # Update the puzzle's candidates
        for idx, candidate_list in enumerate(grid_dict["candidate_values"]):
            if len(candidate_list) != 0:
                cell = Cell(idx)
                grid.modify.add_candidates(candidate_list, cell)

        return grid

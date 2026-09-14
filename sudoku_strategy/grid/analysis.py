from typing import TYPE_CHECKING

from .cell import Cell
from .cell_groups import CellGroups
from .state import GridState

if TYPE_CHECKING:
    from .cell_candidates import CellCandidates
    from .cells import Cells


class GridAnalysis:
    """Perform an analysis of a grid."""

    def __init__(self, state: GridState, cell_groups: CellGroups | None = None):
        self._state = state
        self.cell_groups = cell_groups or CellGroups(state)

    def get_cells_with_candidate(self, cells: Cells, digit: int) -> Cells:
        """Get the cells with a given candidate.

        Out of the cells given, return those that have the given digit as a
        candidate.

        Args:
            cells: The cells to check
            digit: The candidate to check for

        Returns:
            The filtered cells that have the given candidate
        """
        with_candidate = self._state.value_candidates[digit]
        return with_candidate & cells

    def count_cells_with_candidate(self, cells: Cells, digit: int) -> int:
        """Count how many cells have a given candidate.

        Out of the given cells, how many of them have the given digit as a
        candidate.

        Args:
            cells: The cells to check
            digit: The candidate to check for

        Returns:
            The number of cells that have the given candidate
        """
        return len(self.get_cells_with_candidate(cells, digit))

    def get_candidates_for_cell(self, cell: Cell) -> CellCandidates:
        """Return the candidates for a given cell.

        Args:
            cell: The cell to get the candidates for

        Returns:
            The candidates in the given cell
        """
        return self._state.cell_candidates[cell.index]

    def count_candidates_in_cell(self, cell: Cell) -> int:
        """Count the number of candidates in a cell.

        Args:
            cell: The cell to count candidates in
        """
        return len(self.get_candidates_for_cell(cell))

    def get_digit_in_cell(self, cell: Cell) -> int:
        """Get the digit in a cell.

        If the cell has no digit, return 0.

        Args:
            cell: The cell to get the digit for

        Returns:
            The digit in the cell, or 0 if empty
        """
        return self._state.digits[cell.index]

    def cell_has_candidate(self, cell: Cell, digit: int) -> bool:
        """Return True if the given cell has the given candidate.

        Args:
            cell: The cell to check for the candidate
            digit: The candidate to check the cell for

        Returns:
            True if the given cell has the given candidate
        """
        candidates = self._state.cell_candidates[cell.index]
        return digit in candidates

    def is_puzzle_digit(self, cell: Cell) -> bool:
        """Return True if the given cell is set in the original puzzle.

        Args:
            cell: The cell to check for being in the original puzzle

        Returns:
            True if the given cell was set in the original puzzle
        """
        puzzle_digit = self._state.puzzle_digits[cell.index]
        return bool(puzzle_digit)

    def is_complete(self) -> bool:
        """Has the grid been filled with a valid solution.

        If the grid is not full, or not value, return False, otherwise, return
        True.

        Returns:
            True if the sudoku is complete and valid, otherwise False
        """
        if len(self._state.filled_cells) != 81:
            return False

        rows = [0] * 9
        cols = [0] * 9
        boxes = [0] * 9

        for cell in self.cell_groups.cells():
            digit = self.get_digit_in_cell(cell)

            bit = 1 << (digit - 1)

            if (rows[cell.row] | cols[cell.col] | boxes[cell.box]) & bit:
                return False

            rows[cell.row] |= bit
            cols[cell.col] |= bit
            boxes[cell.box] |= bit

        return True

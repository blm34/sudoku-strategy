from __future__ import annotations

from typing import TYPE_CHECKING

from .cell_candidates import CellCandidates
from .cell_groups import CellGroups
from .cells import Cells

if TYPE_CHECKING:
    from collections.abc import Iterable

    from sudoku_strategy.strategy.deduction import Deduction

    from .cell import Cell
    from .state import GridState


class GridModifier:
    """Modify a given grid's state."""

    def __init__(
        self,
        state: GridState,
        cell_groups: CellGroups | None = None,
    ):
        self._state = state
        self._cell_groups = cell_groups or CellGroups(state)

    def _set_digit(self, digit: int, cell_index: int):
        """Update grid state digits with the given digit.

        Args:
            digit: The digit to add
            cell_index: The index of the cell to write the digit to
        """
        self._state.digits[cell_index] = digit

    def _add_cell_to_filled_cells(self, cell: Cell):
        """Update grid state filled cells to include the given cell.

        Args:
            cell: The cell to mark is filled
        """
        self._state.filled_cells += cell

    def _clear_candidates_in_cell(self, cell: Cell):
        """Remove all candidates from the given cell.

        Args:
            cell: The index of the cell to remove all candidates from
        """
        for digit in self._state.cell_candidates[cell.index]:
            self._state.value_candidates[digit] -= cell

        self._state.cell_candidates[cell.index].remove_all()

    def write_digit(self, digit: int, cell: Cell):
        """Write the given digit to the given cell and remove all its candidates.

        Args:
            digit: The digit to write to the cell
            cell: The cell to write the digit to
        """
        self._set_digit(digit, cell.index)
        self._add_cell_to_filled_cells(cell)
        self._clear_candidates_in_cell(cell)

    def update_candidates(self, digit: int, cell: Cell):
        """Update candidates based on a digit in a cell.

        Remove the digit as a candidate from all cells that are peers of the
        given cell.

        Args:
            digit: The digit in the cell causing eliminations
            cell: The cell whose peers are to be updated
        """
        peers = self._cell_groups.peers(cell)
        cells_with_candidate = self._state.value_candidates[digit]
        cells_to_update = peers & cells_with_candidate

        for cell_to_update in cells_to_update:
            self.remove_candidate(digit, cell_to_update)

    def remove_candidate(self, digit: int, cell: Cell):
        """Remove a candidate from a cell.

        If the given cell does not have the given candidate, no action is taken.

        Args:
            digits: The digits of the candidate to remove
            cell: The cell to remove the candidate from
        """
        self._state.cell_candidates[cell.index] -= digit
        self._state.value_candidates[digit] -= cell

    def remove_candidates(self, digits: Iterable[int], cell: Cell):
        """Remove candidates from a cell.

        Args:
            digits: A list of candidates to remove from the cell
            cell: The cell to remove the candidates from
        """
        candidates_to_remove = CellCandidates.from_digits(digits)

        for digit in candidates_to_remove:
            self._state.value_candidates[digit] -= cell

        self._state.cell_candidates[cell.index] &= ~candidates_to_remove

    def add_candidate(self, digit: int, cell: Cell):
        """Add a cadidate to a cell.

        Args:
            digit: The digit of the cadidate to add
            cell: The cell to add the candidate to
        """
        self._state.cell_candidates[cell.index] += digit
        self._state.value_candidates[digit] += cell

    def add_candidates(self, digits: Iterable[int], cell: Cell):
        """Add candidates to a cell.

        Args:
            digits: A list of candidates to add to the cell
            cell: The cell to add the candidates to
        """
        candidates_to_add = CellCandidates.from_digits(digits)

        for digit in candidates_to_add:
            self._state.value_candidates[digit] += cell

        self._state.cell_candidates[cell.index] |= candidates_to_add

    def apply(self, deduction: Deduction):
        """Apply a deduction to a grid.

        Args:
            deduction: The deduction to apply
        """
        if deduction.assignment is not None:
            self.write_digit(deduction.assignment.digit, deduction.assignment.cell)

        for elimination in deduction.eliminations:
            self.remove_candidate(elimination.digit, elimination.cell)

    def compute_candidates(self):
        """Compute all candidates based off the current digits in the grid."""
        for cell in self._cell_groups.filled_cells():
            self._state.cell_candidates[cell.index] = CellCandidates.empty()

        for cell in self._cell_groups.empty_cells():
            self._state.cell_candidates[cell.index] = CellCandidates.with_all()

        for cell in self._cell_groups.filled_cells():
            digit = self._state.digits[cell.index]
            self.update_candidates(digit, cell)

    def reset(self):
        """Reset grid to its starting state."""
        self._state.digits = list(self._state.puzzle_digits)
        self._state.cell_candidates = [CellCandidates.empty() for _ in range(81)]

        self._state.value_candidates = [Cells() for _ in range(10)]
        self._state.fill_filled_cells()

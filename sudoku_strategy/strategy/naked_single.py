from typing import TYPE_CHECKING

from .abs_strategy import AbsStrategy
from .deduction import CellDigit, Deduction

if TYPE_CHECKING:
    from sudoku_strategy.grid import Cell, GridAnalysis


class NakedSingleStrategy(AbsStrategy):
    """Detect naked singles in a sudoku grid."""

    def find(self, analysis: GridAnalysis) -> Deduction | None:
        """Check the grid for naked singles."""
        cell = self._find_naked_single_cell(analysis)

        if cell is None:
            return None

        digit = self._get_value_of_naked_single(analysis, cell)

        return Deduction(
            strategy="Naked Single",
            assignment=CellDigit(cell=cell, digit=digit),
            explanation=f"Cell {cell} is a naked single with value {digit}.",
        )

    def _find_naked_single_cell(self, analysis: GridAnalysis) -> Cell | None:
        """Locate the cell that has a naked single.

        If none are found, returns None.

        Returns:
            A cell that contains a naked single
        """
        for cell in analysis.cell_groups.empty_cells():
            if analysis.count_candidates_in_cell(cell) == 1:
                return cell
        return None

    def _get_value_of_naked_single(self, analysis: GridAnalysis, cell: Cell) -> int:
        """Get the value of a naked single.

        The given ``cell`` must be a naked single - return it's one candidate

        Args:
            cell: The cell that contains a naked single

        Returns:
            The value of the naked single
        """
        candidates = analysis.get_candidates_for_cell(cell)
        return candidates.first()

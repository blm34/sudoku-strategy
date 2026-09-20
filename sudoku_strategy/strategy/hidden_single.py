from typing import TYPE_CHECKING

from sudoku_strategy.strategy.abs_strategy import AbsStrategy
from sudoku_strategy.strategy.deduction import CellDigit, Deduction

if TYPE_CHECKING:
    from sudoku_strategy.grid import GridAnalysis


class HiddenSingleStrategy(AbsStrategy):
    """Detect hidden singles in a sudoku grid."""

    def find(self, analysis: GridAnalysis) -> Deduction | None:
        """Check the grid for hidden singles."""
        result = self._find_hidden_single(analysis)

        if result is None:
            return None

        return Deduction(
            strategy="Hidden Single",
            assignment=result,
            explanation=f"{result.digit} is a hidden single in cell {result.cell}",
        )

    def _find_hidden_single(self, analysis: GridAnalysis) -> CellDigit | None:
        """Find a cell containing a hidden single.

        If none are found returns (None, None)

        Returns:
            The cell containing a hidden single and it's value
        """
        for cells in analysis.cell_groups.units():
            for digit in range(1, 10):
                candidate_cells = analysis.get_cells_with_candidate(cells, digit)
                if len(candidate_cells) == 1:
                    return CellDigit(
                        cell=candidate_cells.first(),
                        digit=digit,
                    )
        return None

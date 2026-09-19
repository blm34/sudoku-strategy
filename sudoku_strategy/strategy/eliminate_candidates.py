from typing import TYPE_CHECKING

from .abs_strategy import AbsStrategy
from .deduction import CellDigit, Deduction

if TYPE_CHECKING:
    from sudoku_strategy.grid import GridAnalysis


class EliminateCandidatesStrategy(AbsStrategy):
    """Detect candidates that can be trivially eliminated."""

    def find(self, analysis: GridAnalysis) -> Deduction | None:
        """Check the grid for candidates to eliminate."""
        eliminations = self._get_eliminatable_candidates(analysis)

        if len(eliminations) == 0:
            return None

        return Deduction(
            strategy="Candidate Elimination",
            explanation="The given candidates are already accounted for in a given unit",
            eliminations=eliminations,
        )

    def _get_eliminatable_candidates(
        self,
        analysis: GridAnalysis,
    ) -> list[CellDigit]:
        """Find all candidates that can be trivially eliminated."""
        cells = []

        for cell in analysis.cell_groups.filled_cells():
            digit = analysis.get_digit_in_cell(cell)
            peers = analysis.cell_groups.peers(cell)
            eliminatable = analysis.get_cells_with_candidate(peers, digit)
            cells += [CellDigit(cell=cell, digit=digit) for cell in eliminatable]

        return cells

from logging import getLogger
from typing import TYPE_CHECKING

from sudoku_strategy.strategy import (
    EliminateCandidatesStrategy,
    HiddenSingleStrategy,
    NakedSingleStrategy,
    PointingPairStrategy,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

    from sudoku_strategy.grid import Grid
    from sudoku_strategy.strategy.abs_strategy import AbsStrategy
    from sudoku_strategy.strategy.deduction import Deduction


_logger = getLogger(__name__)


STRATEGIES = (
    EliminateCandidatesStrategy(),
    NakedSingleStrategy(),
    HiddenSingleStrategy(),
    PointingPairStrategy(),
)


class Solver:
    def __init__(self, strategies: Sequence[AbsStrategy] = STRATEGIES):
        self._strategies = strategies

    def find_next(self, grid: Grid) -> Deduction | None:
        """Find the next move for the given grid.

        Args:
            grid: The grid to find the next move for

        Returns:
            The next move, or None if none are found
        """
        for strategy in self._strategies:
            deduction = strategy.find(grid.analyse)

            if deduction is not None:
                return deduction

        return None

    def solve(self, grid: Grid) -> list[Deduction]:
        """Find all the moves to solve the sudoku.

        Args:
            grid: The state of the puzzle to be solved

        Returns:
            A list of moves to solve the puzzle
        """
        working_grid = grid.copy()
        deductions = []

        while not working_grid.analyse.is_complete():
            deduction = self.find_next(working_grid)

            if deduction is None:
                _logger.warning("No next step found for puzzle.")
                break

            deductions.append(deduction)

            working_grid.modify.apply(deduction)

        return deductions

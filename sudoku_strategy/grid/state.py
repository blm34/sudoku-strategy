from typing import TYPE_CHECKING

from .cell import Cell
from .cell_candidates import CellCandidates
from .cells import Cells

if TYPE_CHECKING:
    from typing import Self


class GridState:
    """Store grid state and provide information about candidates.

    Attributes:
        digits: The list of digits in the grid
        puzzle_digits: The list of digits for the starting puzzle state
        cell_candidates: The list of candidates for each cell
        value_candidates: A list of cell groups for locations of each digit
            candidate. Indexed by digit (index 0 is ignored)
        filled_cells: The cells that have a digit filled

    Methods:
        create_empty
        new_puzzle
        copy
        fill_filled_cells
        fill_value_candidates
    """

    def __init__(
        self,
        digits: list[int],
        candidates: list[CellCandidates],
        puzzle_digits: tuple[int, ...],
    ):
        """Initialise a GridState object.

        Args:
            digits: The list of digits in the grid
            candidates: The list of candidates for each cell
            puzzle_digits: The list of digits for the starting puzzle state
        """
        # Definitions of the grid state
        self.digits = digits
        self.puzzle_digits = puzzle_digits
        self.cell_candidates = candidates

        # Extra (redundant) information allowing for increased efficiency
        self.value_candidates = self.fill_value_candidates()
        self.filled_cells = self.fill_filled_cells()

    @classmethod
    def create_empty(cls) -> Self:
        """Initialise an empty puzzle grid.

        Returns:
            A GridState containing no values or candidates"""
        return cls(
            digits=[0] * 81,
            candidates=[CellCandidates.empty() for _ in range(81)],
            puzzle_digits=tuple([0] * 81),
        )

    @classmethod
    def new_puzzle(cls, puzzle_digits: tuple[int, ...]) -> Self:
        """Initialise a new puzzle with no values entered.

        Args:
            puzzle_digits: The digits for the puzzle to start with

        Returns:
            The grid state for the starting state of the puzzle"""
        if len(puzzle_digits) != 81:
            raise ValueError("Sudoku puzzle must have 81 cells.")

        return cls(
            digits=list(puzzle_digits),
            candidates=[CellCandidates.empty() for _ in range(81)],
            puzzle_digits=puzzle_digits,
        )

    def copy(self) -> GridState:
        """Creates a copy of the current grid state.

        Returns:
            The copied GridState"""
        return GridState(
            digits=self.digits.copy(),
            candidates=self.cell_candidates.copy(),
            puzzle_digits=self.puzzle_digits,
        )

    def fill_value_candidates(self) -> list[Cells]:
        """Fill in value_candidates using the contents of cell_candidates.

        Changes in place and returns the resulting value.

        Returns:
            The resulting contents of `value_candidates`
        """
        self.value_candidates = [Cells() for _ in range(10)]

        for idx, candidates in enumerate(self.cell_candidates):
            for digit in candidates:
                self.value_candidates[digit] += Cell(idx)

        return self.value_candidates

    def fill_filled_cells(self) -> Cells:
        """Fill out filled_cells from the contents of digits.

        Changes in place and returns the resulting cells

        Returns:
            The resulting value of `filled_cells`
        """
        self.filled_cells = Cells()
        for idx, digit in enumerate(self.digits):
            if digit:
                self.filled_cells += Cell(idx)

        return self.filled_cells

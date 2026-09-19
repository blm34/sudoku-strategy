from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Self


@dataclass(frozen=True)
class Cell:
    """Represent a single cell in a sudoku grid.

    The indexes start from 0 in the top left cell and work along each row
    and then down each column up to 80 in the bottom left cell. Rows and columns
    are zero indexed. Boxes are indexed 1-8 with one being top left, then working
    along each row.

    Properties:
        index: The index of the cell in the grid (0-80)
        row: The row of the cell (0-8)
        col: The column of the cell (0-8)
        box: The index of the box containing the cel (0-8)

    Methods:
        from_position
    """

    index: int

    def __post_init__(self):
        if not (0 <= self.index <= 80):
            raise ValueError(
                f"Cell index must be in the range 0-80. '{self.index}' is not valid."
            )

    @classmethod
    def from_position(cls, row: int, col: int) -> Self:
        """Create a cell from it's position on the board.

        Args:
            row: The row for the cell (0-8)
            col: The column for the cell (0-8)

        Returns:
            A `Cell` for the given position
        """
        if not (0 <= row <= 8 and 0 <= col <= 8):
            raise ValueError(
                "Row and column for a cell must be in the range 0-8. "
                f"({row}, {col}) is not valid."
            )

        index = row * 9 + col
        return cls(index)

    @property
    def row(self) -> int:
        """The row the cell is in (0-8).

        Top row is `0`, bottom row is `8`.
        """
        return self.index // 9

    @property
    def col(self) -> int:
        """The column the cell is in (0-8).

        The left most column is `0`, the right most column is `8`.
        """
        return self.index % 9

    @property
    def box(self) -> int:
        """The index of the box the cell is in (0-8).

        Box 0 is top left, with 1 to its right, down to box 8 in the bottom
        right.
        """
        return (self.row // 3) * 3 + self.col // 3

    def __str__(self) -> str:
        """Represent a cell in 'R4C8' format."""
        return f"R{self.row + 1}C{self.col + 1}"

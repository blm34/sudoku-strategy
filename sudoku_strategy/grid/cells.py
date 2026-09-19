from typing import TYPE_CHECKING

from .cell import Cell

if TYPE_CHECKING:
    from collections.abc import Iterator
    from typing import Self


class Cells:
    """Representation of a collection of cells.

    Cells are represented by a bit mask. Bits are set in positions corresponding
    to the indexes of cells that are included. The least significant bit
    corresponds to cell index 0.
    """

    # Bit mask of 1s in every position that could be set
    _MASK = (1 << 81) - 1

    def __init__(self, mask: int = 0):
        """Create a Cells object from the given bit mask.

        Defaults to a collection of no cells.

        Args:
            mask: The bit mask to use."""
        self._mask = mask

    def _mask_for_cell(self, cell: Cell) -> int:
        """Get the mask for the given cell.

        Args:
            cell: The cell to get a bit mask for

        Returns:
            The bit mask representing the one given cell"""
        return 1 << cell.index

    def __isub__(self, cell: Cell) -> Self:
        """Remove the given cell in place."""
        mask = self._mask_for_cell(cell)
        self._mask &= ~mask
        return self

    def __sub__(self, cell: Cell) -> Cells:
        """Make a new Cells object with the given cell removed."""
        cell_mask = self._mask_for_cell(cell)
        mask = self._mask & ~cell_mask
        return Cells(mask)

    def __iadd__(self, cell: Cell) -> Self:
        """Add the given cell in place."""
        mask = self._mask_for_cell(cell)
        self._mask |= mask
        return self

    def __add__(self, cell: Cell) -> Cells:
        """Make a new Cells object with the given cell added."""
        cell_mask = self._mask_for_cell(cell)
        mask = self._mask | cell_mask
        return Cells(mask)

    def __and__(self, other: Cells) -> Cells:
        """Performs an intersection on two sets of cells."""
        mask = self._mask & other._mask
        return Cells(mask)

    def __or__(self, other: Cells) -> Cells:
        """Performs a union on two sets of cells."""
        mask = self._mask | other._mask
        return Cells(mask)

    def __invert__(self) -> Cells:
        """Returns the complementary set of cells."""
        mask = ~self._mask & self._MASK
        return Cells(mask)

    def __len__(self) -> int:
        """Counts number of cells in the set."""
        return self._mask.bit_count()

    def __contains__(self, cell: Cell) -> bool:
        """Checks if the set contains the given cell."""
        cell_mask = self._mask_for_cell(cell)
        return bool(cell_mask & self._mask)

    def __iter__(self) -> Iterator[Cell]:
        """Iterate over the cells in the set."""
        mask = self._mask

        while mask:
            bit = mask & -mask
            index = bit.bit_length() - 1
            yield Cell(index)
            mask ^= bit

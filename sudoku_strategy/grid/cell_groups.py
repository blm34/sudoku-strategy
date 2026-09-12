from __future__ import annotations

from typing import TYPE_CHECKING

from .cells import Cells

if TYPE_CHECKING:
    from .cell import Cell
    from .state import GridState


class CellGroups:
    """Contains iterators over regions of the grid.

    Methods:
        cells
        empty_cells
        filled_cells
        units
        lines
        row
        col
        box
        peers
    """

    _ALL_CELLS = (1 << 81) - 1
    _ROW_MASKS = tuple(((1 << 9) - 1) << row * 9 for row in range(9))
    _COL_MASKS = tuple(
        sum(1 << (col + 9 * row) for row in range(9)) for col in range(9)
    )
    _BOX_MASKS = tuple(
        sum(
            1 << (row * 9 + col)
            for row in range(box_row * 3, box_row * 3 + 3)
            for col in range(box_col * 3, box_col * 3 + 3)
        )
        for box_row in range(3)
        for box_col in range(3)
    )

    def __init__(self, grid_state: GridState):
        """Initialise a CellGroups object.

        Args:
            grid_state: The grid state to use for state specific groups"""
        self._state = grid_state

    def cells(self) -> Cells:
        """Get all cells in the grid.

        Returns:
            All the cells in the grid
        """
        return Cells(self._ALL_CELLS)

    def empty_cells(self) -> Cells:
        """Get all the empty cells in the grid.

        Returns:
            All the empty cells in the grid
        """
        return ~self._state.filled_cells

    def filled_cells(self) -> Cells:
        """Get all non-empty cells in the grid.

        Returns:
            All cells containing values
        """
        return self._state.filled_cells

    def units(self) -> tuple[Cells, ...]:
        """Get a tuple of all rows, cols, and boxes.

        Returns:
            A tuple containing all units in a grid"""
        return tuple(
            unit
            for idx in range(9)
            for unit in (self.row(idx), self.col(idx), self.box(idx))
        )

    def lines(self) -> tuple[Cells, ...]:
        """Get a tuple of all rows and columns.

        Returns:
            A tuple of all the rows and columns in a grid"""
        return tuple(
            unit for idx in range(9) for unit in (self.row(idx), self.col(idx))
        )

    def row(self, row_num: int) -> Cells:
        """Get the cells for the given row.

        Args:
            row_num: The row to get the cells from

        Returns:
            The cells in the given row
        """
        mask = self._ROW_MASKS[row_num]
        return Cells(mask)

    def col(self, col_num: int) -> Cells:
        """Get the cells for the given column.

        Args:
            col_num: The column to get the cells from

        Returns:
            The cells in the given column
        """
        mask = self._COL_MASKS[col_num]
        return Cells(mask)

    def box(self, box_num: int) -> Cells:
        """Get the cells for the given box.

        Args:
            box_num: The index of the box to get the cells from

        Returns:
            The cells in the given box
        """
        mask = self._BOX_MASKS[box_num]
        return Cells(mask)

    def peers(self, cell: Cell) -> Cells:
        """Get all the peers of a given cell.

        Args:
            cell: The cell to find peers of

        Returns:
            The cells that are peers of the given cell
        """
        return (self.row(cell.row) | self.col(cell.col) | self.box(cell.box)) - cell

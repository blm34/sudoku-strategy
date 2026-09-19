from unittest.mock import MagicMock, Mock

import pytest

from sudoku_strategy.grid import Cell, Cells, GridState
from sudoku_strategy.grid.cell_groups import CellGroups


class TestCellGroups:
    @pytest.fixture
    def state(self):
        return Mock(GridState)

    @pytest.fixture
    def cell_groups(self, state):
        return CellGroups(state)

    def test_cells_returns_81_cells(self, cell_groups):
        # ACT
        cells = cell_groups.cells()

        # ASSERT
        assert len(cells) == 81

    def test_empty_cells_returns_filled_cells_inverted(self, cell_groups, state):
        # ARRANGE
        state = cell_groups._state
        filled_cells = MagicMock(Cells)
        empty_cells = MagicMock(Cells)
        filled_cells.__invert__.return_value = empty_cells
        state.filled_cells = filled_cells

        # ACT
        cells = cell_groups.empty_cells()

        # ASSERT
        assert cells is empty_cells
        filled_cells.__invert__.assert_called_once()

    def test_filled_cells_returns_grid_state_filled_cells(self, cell_groups, state):
        # ARRANGE
        state = cell_groups._state
        filled_cells = Mock(Cells)
        state.filled_cells = filled_cells

        # ACT
        cells = cell_groups.filled_cells()

        # ASSERT
        assert cells is filled_cells

    def test_units_produces_27_units_with_nine_values(self, cell_groups):
        # ACT
        units = cell_groups.units()

        # ASSERT
        assert len(units) == 27
        assert all(len(unit) == 9 for unit in units)

    def test_lines_produces_18_units_with_nine_values(self, cell_groups):
        # ACT
        units = cell_groups.lines()

        # ASSERT
        assert len(units) == 18
        assert all(len(unit) == 9 for unit in units)

    @pytest.mark.parametrize("row", range(9))
    def test_rows_have_nine_values(self, row, cell_groups):
        # ACT
        cells = cell_groups.row(row)

        # ASSERT
        assert len(cells) == 9

    def test_row_zero_contains_expected_cells(self, cell_groups):
        # ACT
        cells = cell_groups.row(0)

        # ASSERT
        for idx, cell in enumerate(cells):
            assert cell.index == idx

    @pytest.mark.parametrize("col", range(9))
    def test_cols_have_with_nine_values(self, col, cell_groups):
        # ACT
        cells = cell_groups.col(col)

        # ASSERT
        assert len(cells) == 9

    def test_col_zero_contains_expected_cells(self, cell_groups):
        # ACT
        cells = cell_groups.col(0)

        # ASSERT
        for idx, cell in enumerate(cells):
            assert cell.index == idx * 9

    @pytest.mark.parametrize("box", range(9))
    def test_boxes_have_nine_values(self, box, cell_groups):
        # ACT
        cells = cell_groups.box(box)

        # ASSERT
        assert len(cells) == 9

    def test_first_box_contains_expected_cells(self, cell_groups):
        # ARRANGE
        expected_indexes = (0, 1, 2, 9, 10, 11, 18, 19, 20)

        # ACT
        cells = cell_groups.box(0)

        # ASSERT
        for idx, cell in enumerate(cells):
            assert cell.index == expected_indexes[idx]

    def test_peers_combine_row_col_and_box_and_excludes_cell(self, cell_groups):
        # ARRANGE
        class FakeCells(set):
            def __or__(self, other):
                return FakeCells(super().__or__(other))

            def __sub__(self, other):
                return FakeCells(cell for cell in self if cell != other)

        cell = Mock(Cell, row=0, col=8, box=2)

        shared_cell = Mock(Cell)
        row_cell = Mock(Cell)
        col_cell = Mock(Cell)
        box_cell = Mock(Cell)

        row = FakeCells({shared_cell, cell, row_cell})
        col = FakeCells({shared_cell, cell, col_cell})
        box = FakeCells({shared_cell, cell, box_cell})

        cell_groups.row = Mock(return_value=row)
        cell_groups.col = Mock(return_value=col)
        cell_groups.box = Mock(return_value=box)

        # ACT
        peers = cell_groups.peers(cell)

        # ASSERT
        assert peers == {shared_cell, row_cell, col_cell, box_cell}
        cell_groups.row.assert_called_once_with(0)
        cell_groups.col.assert_called_once_with(8)
        cell_groups.box.assert_called_once_with(2)

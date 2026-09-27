import pytest

from sudoku_strategy.grid import Cell, Cells, GridState
from sudoku_strategy.grid.cell_groups import CellGroups


class TestCellGroups:
    @pytest.fixture
    def state(self):
        return GridState.create_empty()

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
        state.filled_cells = Cells(0b00101100101010100100001110)

        # ACT
        cells = cell_groups.empty_cells()

        # ASSERT
        assert cells._mask == (~state.filled_cells)._mask

    def test_filled_cells_returns_grid_state_filled_cells(self, cell_groups, state):
        # ACT
        cells = cell_groups.filled_cells()

        # ASSERT
        assert cells is state.filled_cells

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
        cell = Cell(8)

        # ACT
        peers = cell_groups.peers(cell)

        # ASSERT
        assert len(peers) == 20
        assert cell not in peers

        for peer in peers:
            assert peer.row == cell.row or peer.col == cell.col or peer.box == cell.box

from itertools import product

import pytest

from sudoku_strategy.grid.cell import Cell


class TestCell:
    @pytest.mark.parametrize("index", (-10, -1, 81, 90))
    def test_valueerror_raised_for_index_out_of_range(self, index):
        # ARRANGE
        expected_message = (
            f"Cell index must be in the range 0-80. '{index}' is not valid."
        )

        # ACT
        with pytest.raises(ValueError) as exc:
            Cell(index)

        # ASSERT
        assert str(exc.value) == expected_message

    @pytest.mark.parametrize("index", range(81))
    def test_valid_indexes_produce_correct_cell(self, index):
        # ACT
        cell = Cell(index)

        # ASSERT
        assert cell.index == index

    @pytest.mark.parametrize(
        ("row", "col"),
        list(product(range(8), range(8))),
    )
    def test_from_position_creates_correct_cell(self, row, col):
        # ACT
        cell = Cell.from_position(row, col)

        # ASSERT
        assert cell.row == row
        assert cell.col == col

    @pytest.mark.parametrize(
        ("row", "col"),
        (
            (-1, -1),
            (0, -1),
            (-1, 0),
            (9, 8),
            (8, 9),
            (9, 9),
            (5, 11),
        ),
    )
    def test_from_position_raises_value_error_for_invalid_position(self, row, col):
        # ARRANGE
        expected_message = f"Row and column for a cell must be in the range 0-8. ({row}, {col}) is not valid."

        # ACT
        with pytest.raises(ValueError) as exc:
            Cell.from_position(row, col)

        # ASSERT
        assert str(exc.value) == expected_message

    @pytest.mark.parametrize(
        ("index", "expected_row"),
        (
            (0, 0),
            (8, 0),
            (9, 1),
            (40, 4),
            (71, 7),
            (72, 8),
            (80, 8),
        ),
    )
    def test_row(self, index, expected_row):
        # ARRANGE
        cell = Cell(index)

        # ACT
        row = cell.row

        # ASSERT
        assert row == expected_row

    @pytest.mark.parametrize(
        ("index", "expected_col"),
        (
            (0, 0),
            (8, 8),
            (10, 1),
            (40, 4),
            (71, 8),
            (75, 3),
            (80, 8),
        ),
    )
    def test_col(self, index, expected_col):
        # ARRANGE
        cell = Cell(index)

        # ACT
        col = cell.col

        # ASSERT
        assert col == expected_col

    @pytest.mark.parametrize(
        ("row", "col", "expected_box"),
        [
            (0, 0, 0),
            (0, 2, 0),
            (0, 3, 1),
            (2, 8, 2),
            (3, 0, 3),
            (4, 4, 4),
            (5, 8, 5),
            (6, 0, 6),
            (8, 8, 8),
        ],
    )
    def test_box(self, row, col, expected_box):
        # ARRANGE
        cell = Cell.from_position(row, col)

        # ACT
        box = cell.box

        # ASSERT
        assert box == expected_box

    @pytest.mark.parametrize("index", range(81))
    def test_equal_cells_are_equal(self, index):
        # ARRANGE
        first = Cell(index)
        second = Cell(index)

        # ACT & ASSERT
        assert first == second

    @pytest.mark.parametrize(
        ("row", "col", "expected_string"),
        (
            (0, 0, "R1C1"),
            (8, 0, "R9C1"),
            (5, 3, "R6C4"),
            (8, 8, "R9C9"),
            (7, 2, "R8C3"),
        ),
    )
    def test_str(self, row, col, expected_string):
        # ARRANGE
        cell = Cell.from_position(row, col)

        # ACT
        string = str(cell)

        # ASSERT
        assert string == expected_string

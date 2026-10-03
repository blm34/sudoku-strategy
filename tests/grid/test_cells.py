from unittest.mock import Mock

import pytest

from sudoku_strategy.grid import Cell
from sudoku_strategy.grid.cells import Cells, CellsEmptyException


class TestCells:
    @pytest.fixture
    def cells_empty(self):
        return Cells.empty()

    @pytest.fixture
    def cells_full(self):
        return Cells.with_all()

    def test_cells_uses_passed_mask(self):
        # ARRANGE
        mask = Mock(int)

        # ACT
        cells = Cells(mask)

        # ASSERT
        assert cells._mask is mask

    def test_with_all_contains_all_cells(self):
        # ACT
        cells = Cells.with_all()

        # ASSERT
        assert len(cells) == 81

    def test_with_all_gives_the_complement_of_empty(self, cells_empty):
        # ARRANGE
        expected_cells = ~cells_empty

        # ACT
        cells = Cells.with_all()

        # ASSERT
        assert cells == expected_cells

    @pytest.mark.parametrize(
        ("mask", "index"),
        (
            (0b100, 2),
            (0b10010, 1),
            (0b11111, 0),
            (0b101011000000, 6),
        ),
    )
    def test_first_returns_first_cell_in_cells(self, mask, index):
        # ARRANGE
        cells = Cells(mask)

        # ACT
        first = cells.first()

        # ASSERT
        assert first.index == index

    def test_first_raises_error_when_no_cells_present(self, cells_empty):
        with pytest.raises(CellsEmptyException):
            # ACT
            cells_empty.first()

    @pytest.mark.parametrize(
        ("index", "expected_mask"),
        (
            (0, 0b1),
            (1, 0b10),
            (2, 0b100),
            (3, 0b1000),
            (4, 0b10000),
        ),
    )
    def test_mask_for_cell_gives_correct_bit_mask(
        self, index, expected_mask, cells_empty
    ):
        # ARRANGE
        cell = Cell(index)

        # ACT
        mask = cells_empty._mask_for_cell(cell)

        # ASSERT
        assert mask == expected_mask

    def test_subtract_in_place_removes_one_cell(self, cells_full):
        # ARRANGE
        cell = Cell(80)

        # ACT
        cells_full -= cell

        # ASSERT
        assert len(cells_full) == 80
        assert cell not in cells_full

    def test_subtract_removes_cell(self, cells_full):
        # ARRANGE
        cell = Cell(40)

        # ACT
        new_cells = cells_full - cell

        # ASSERT
        assert len(new_cells) == 80
        assert cell not in new_cells

    def test_subtract_makes_a_new_object(self, cells_full):
        # ARRANGE
        cell = Cell(30)

        # ACT
        new_cells = cells_full - cell

        # ASSERT
        assert cells_full is not new_cells

    def test_add_in_place_adds_cell(self, cells_empty):
        # ARRANGE
        cell = Cell(4)

        # ACT
        cells_empty += cell

        # ASSERT
        assert len(cells_empty) == 1
        assert cell in cells_empty

    def test_add_in_place_does_not_remove_existing_cells(self):
        # ARRANGE
        existing_cell = Cell(0)
        new_cell = Cell(5)
        cells = Cells(1 << existing_cell.index)

        # ACT
        cells += new_cell

        # ASSERT
        assert len(cells) == 2
        assert existing_cell in cells
        assert new_cell in cells

    def test_add_adds_cells(self, cells_empty):
        # ARRANGE
        cell = Cell(3)

        # ACT
        new_cells = cells_empty + cell

        # ASSERT
        assert len(new_cells) == 1
        assert cell in new_cells

    def test_add_does_not_remove_existing_cells(self):
        # ARRANGE
        existing_cell = Cell(0)
        new_cell = Cell(2)
        cells = Cells(1 << existing_cell.index)

        # ACT
        new_cells = cells + new_cell

        # ASSERT
        assert len(new_cells) == 2
        assert existing_cell in new_cells
        assert new_cell in new_cells

    def test_add_creates_a_new_object(self, cells_empty):
        # ARRANGE
        cell = Cell(80)

        # ACT
        new_cells = cells_empty + cell

        # ASSERT
        assert new_cells is not cells_empty

    def test_and_returns_intersection(self):
        # ARRANGE
        first_mask = (1 << 0) | (1 << 40) | (1 << 80)
        second_mask = (1 << 0) | (1 << 10) | (1 << 80)
        resultant_mask = (1 << 0) | (1 << 80)
        first = Cells(first_mask)
        second = Cells(second_mask)

        # ACT
        result = first & second

        # ASSERT
        assert result._mask == resultant_mask

    def test_or_returns_union(self):
        # ARRANGE
        first_mask = (1 << 0) | (1 << 40)
        second_mask = (1 << 40) | (1 << 80)
        resultant_mask = (1 << 0) | (1 << 40) | (1 << 80)
        first = Cells(first_mask)
        second = Cells(second_mask)

        # ACT
        result = first | second

        # ASSERT
        assert result._mask == resultant_mask

    def test_invert_returns_complement(self):
        # ARRANGE
        cell = Cell(40)
        cells = Cells(1 << cell.index)

        # ACT
        result = ~cells

        # ASSERT
        assert len(result) == 80
        assert cell not in result

    def test_invert_of_empty_cells_contains_all_81_cells(self, cells_empty):
        # ACT
        result = ~cells_empty

        # ASSERT
        assert len(result) == 81

    def test_invert_of_all_cells_contains_no_cells(self, cells_full):
        # ACT
        result = ~cells_full

        # ASSERT
        assert len(result) == 0

    def test_len_gives_number_of_cells(self):
        # ARRANGE
        mask = (1 << 0) | (1 << 40) | (1 << 80)
        cells = Cells(mask)

        # ACT
        length = len(cells)

        # ASSERT
        assert length == 3

    def test_contians_checks_cell_is_in_cells(self):
        # ARRANGE
        cell = Cell(48)
        cells = Cells(1 << cell.index)

        # ACT
        contains = cell in cells

        # ASSERT
        assert contains

    def test_contians_checks_cell_is_not_in_cells(self):
        # ARRANGE
        cell = Cell(48)
        other_cell = Cell(38)
        cells = Cells(1 << cell.index)

        # ACT
        contains = other_cell in cells

        # ASSERT
        assert not contains

    def test_iter_gives_expected_cells(self):
        # ARRANGE
        cell_indexes = (0, 13, 44, 75)
        mask = sum(1 << index for index in cell_indexes)
        cells = Cells(mask)

        # ACT
        result = list(cells)

        # ASSERT
        assert all(cell.index in cell_indexes for cell in result)

    def test_cells_iteration_is_reusable(self):
        # ARRANGE
        cells = Cells((1 << 0) | (1 << 40) | (1 << 80))

        # ACT
        first_iteration = list(cells)
        second_iteration = list(cells)

        # ASSERT
        assert first_iteration == second_iteration

    @pytest.mark.parametrize(
        "mask",
        (
            0b0,
            0b11110101110100101011,
            0b1111111100101,
        ),
    )
    def test_eq_is_true_for_cell_with_itself(self, mask):
        # ARRANGE
        cells = Cells(mask)

        # ACT
        equal = cells == cells  # noqa: PLR0124

        # ASSERT
        assert equal

    @pytest.mark.parametrize(
        "mask",
        (
            0b0,
            0b000010011101,
            0b11111,
        ),
    )
    def test_eq_is_true_for_identical_cells(self, mask):
        # ARRANGE
        cells1 = Cells(mask)
        cells2 = Cells(mask)

        # ACT
        equal = cells1 == cells2

        # ASSERT
        assert equal

    @pytest.mark.parametrize(
        "mask",
        (
            0b0,
            0b000010011101,
            0b11111,
        ),
    )
    def test_eq_is_false_for_different_cell_contents(self, mask):
        # ARRANGE
        cells1 = Cells(mask)
        cells2 = Cells(mask + 1)

        # ACT
        equal = cells1 == cells2

        # ASSERT
        assert not equal

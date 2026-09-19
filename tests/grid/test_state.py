from unittest.mock import Mock

import pytest

from sudoku_strategy.grid import CellCandidates
from sudoku_strategy.grid.state import GridState


class TestGridState:
    @pytest.fixture
    def state(self):
        return GridState.create_empty()

    def test_create_empty_initialises_empty_grid_of_digits(self):
        # ACT
        grid = GridState.create_empty()

        # ASSERT
        assert len(grid.digits) == 81
        assert all(digit == 0 for digit in grid.digits)

    def test_create_empty_initialises_empty_grid_of_cell_candidates(self):
        # ACT
        grid = GridState.create_empty()

        # ASSERT
        assert len(grid.cell_candidates) == 81
        assert all(len(candidates) == 0 for candidates in grid.cell_candidates)

    def test_create_empty_initialises_empty_grid_of_value_candidates(self):
        # ACT
        grid = GridState.create_empty()

        # ASSERT
        assert len(grid.value_candidates) == 10
        assert all(len(cells) == 0 for cells in grid.value_candidates)

    def test_create_empty_initialises_empty_grid_of_puzzle_digits(self):
        # ACT
        grid = GridState.create_empty()

        # ASSERT
        assert len(grid.puzzle_digits) == 81
        assert all(digit == 0 for digit in grid.puzzle_digits)

    def test_create_empty_initialises_with_no_filled_cells(self):
        # ACT
        grid = GridState.create_empty()

        # ASSERT
        assert grid.filled_cells._mask == 0

    def test_new_puzzle_adds_digits_to_digits(self):
        # ARRANGE
        digits = [0] * 81
        digits[8] = 1
        digits = tuple(digits)

        # ACT
        grid = GridState.new_puzzle(digits)

        # ASSERT
        assert grid.digits.count(0) == 80
        assert grid.digits[8] == 1

    def test_new_puzzle_sets_all_candidates_to_zero(self):
        # ARRANGE
        digits = (0,) * 81

        # ACT
        grid = GridState.new_puzzle(digits)

        # ASSERT
        assert all(len(candidates) == 0 for candidates in grid.cell_candidates)
        assert all(len(cells) == 0 for cells in grid.value_candidates)

    def test_new_puzzle_sets_puzzle_digits_correctly(self):
        # ARRANGE
        digits = [0] * 81
        digits[8] = 1
        digits = tuple(digits)

        # ACT
        grid = GridState.new_puzzle(digits)

        # ASSERT
        assert grid.puzzle_digits.count(0) == 80
        assert grid.puzzle_digits[8] == 1

    @pytest.mark.parametrize("length", (10, 80, 82, 100))
    def test_new_puzzle_raises_error_when_given_wrong_number_of_digits(self, length):
        # ARRANGE
        digits = (0,) * length

        with pytest.raises(ValueError):
            # ACT
            GridState.new_puzzle(digits)

    def test_copy_returns_same_digits(self, state):
        # ARRANGE
        mock_digits = list(range(81))
        state.digits = mock_digits

        # ACT
        copy = state.copy()

        # ASSERT
        assert copy.digits == mock_digits

    def test_copy_returns_same_candidates(self, state):
        # ARRANGE
        candidate = Mock(CellCandidates)
        candidate.__iter__ = lambda _: iter(range(9))
        state.cell_candidates = [candidate]  # type: ignore[reportAttributeAccessIssue]

        # ACT
        copy = state.copy()

        # ASSERT
        assert copy.cell_candidates == [candidate]

    def test_copy_returns_same_puzzle_digits(self, state):
        # ARRANGE
        puzzle_digits = tuple(range(81))
        state.puzzle_digits = puzzle_digits

        # ACT
        copy = state.copy()

        # ASSERT
        assert copy.puzzle_digits == puzzle_digits

    def test_copy_has_independent_digits(self, state):
        # ARRANGE
        mock_digits = list(range(81))
        state.digits = mock_digits

        # ACT
        copy = state.copy()

        # ASSERT
        assert copy.digits is not mock_digits

    def test_copy_has_independent_candidates(self, state):
        # ARRANGE
        candidate = Mock(CellCandidates)
        candidate.__iter__ = lambda _: iter(range(9))
        state.cell_candidates = [candidate]  # type: ignore[reportAttributeAccessIssue]

        # ACT
        copy = state.copy()

        # ASSERT
        assert copy.cell_candidates is not state.cell_candidates

    def test_fill_value_candidates_adds_candidates_for_correct_digit(self, state):
        # ARRANGE
        mock_candidate = Mock(CellCandidates)
        digit = 5
        mock_candidate.__iter__ = lambda _: iter([digit])
        cell_index = 7
        state.cell_candidates[cell_index] = mock_candidate

        # ACT
        state.fill_value_candidates()

        # ASSERT
        assert state.value_candidates[digit]._mask == 1 << cell_index

    def test_fill_filled_cells_contains_correct_cells(self, state):
        # ARRANGE
        state.digits[5] = 1
        state.digits[20] = 7
        state.digits[59] = 4

        # ACT
        state.fill_filled_cells()

        # ASSERT
        filled = state.filled_cells
        assert filled._mask & 1 << 5
        assert filled._mask & 1 << 20
        assert filled._mask & 1 << 59

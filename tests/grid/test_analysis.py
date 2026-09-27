from unittest.mock import MagicMock, Mock, patch

import pytest

from sudoku_strategy.grid import Cell, CellCandidates, CellGroups, Cells, GridState
from sudoku_strategy.grid.analysis import GridAnalysis


class TestGridAnalysis:
    @pytest.fixture
    def state(self):
        return GridState.create_empty()

    @pytest.fixture
    def cell_groups(self, state):
        return CellGroups(state)

    @pytest.fixture
    def analysis(self, state, cell_groups):
        return GridAnalysis(state, cell_groups)

    def test_get_cells_with_candidate_gets_intersection_of_given_cells_with_cells_with_candidate(
        self,
        analysis,
        state,
    ):
        # ARRANGE
        cells_in = Cells(0b111)
        digit = 4
        state.value_candidates[digit] = CellCandidates(0b1110)

        # ACT
        cells = analysis.get_cells_with_candidate(cells_in, digit)

        # ASSERT
        assert 2 in cells
        assert 3 in cells

        assert 1 not in cells
        assert 4 not in cells

        assert len(cells) == 2

    def test_count_cells_with_candidate_gets_length_of_candidates(self, analysis):
        # ARRANGE
        cells_with_candidate = Cells(0b101010101)

        with patch.object(
            analysis,
            "get_cells_with_candidate",
            return_value=cells_with_candidate,
        ):
            # ACT
            length = analysis.count_cells_with_candidate(Mock(Cells), 2)

        # ASSERT
        assert length == 5

    def test_get_candidates_for_cell_gets_candidates_for_the_cell(
        self,
        analysis,
        state,
    ):
        # ARRANGE
        cell = Cell(17)
        expected_candidates = state.cell_candidates[cell.index]

        # ACT
        candidates = analysis.get_candidates_for_cell(cell)

        # ASSERT
        assert candidates is expected_candidates

    def test_count_candidates_in_cell_gets_length_of_candidates_in_cell(self, analysis):
        # ARRANGE
        cell_candidates = CellCandidates(0b11101111)

        with patch.object(
            analysis,
            "get_candidates_for_cell",
            return_value=cell_candidates,
        ):
            # ACT
            count = analysis.count_candidates_in_cell(Mock(Cell))

        # ASSERT
        assert count == 7

    def test_get_digit_in_cell_gets_digit_in_the_given_cell(self, analysis, state):
        # ARRANGE
        cell = Cell(15)
        expected_digit = state.digits[cell.index]

        # ACT
        digit = analysis.get_digit_in_cell(cell)

        # ASSERT
        assert digit is expected_digit

    @pytest.mark.parametrize("digit", (3, 5, 7, 8))
    def test_cell_has_candidate_true_when_cell_has_candidate(
        self,
        analysis,
        state,
        digit,
    ):
        # ARRANGE
        cell = Cell(26)
        state.cell_candidates[cell.index] = CellCandidates(0b011010100)

        # ACT
        contained = analysis.cell_has_candidate(cell, digit)

        # ASSERT
        assert contained

    @pytest.mark.parametrize("digit", (1, 2, 4, 6, 9))
    def test_cell_has_candidate_false_when_cell_does_not_have_candidate(
        self,
        analysis,
        state,
        digit,
    ):
        # ARRANGE
        cell = Cell(26)
        state.cell_candidates[cell.index] = CellCandidates(0b011010100)

        # ACT
        contained = analysis.cell_has_candidate(cell, digit)

        # ASSERT
        assert not contained

    def test_is_puzzle_digit_returns_true_for_a_puzzle_digit(self, analysis, state):
        # ARRANGE
        state.puzzle_digits = (0,) * 20 + (1,) + (0,) * 60
        cell = Cell(20)

        # ACT
        is_puzzle_digit = analysis.is_puzzle_digit(cell)

        # ASSERT
        assert is_puzzle_digit

    def test_is_puzzle_digit_returns_false_for_a_non_puzzle_digit(
        self,
        analysis,
        state,
    ):
        # ARRANGE
        state.puzzle_digits = (0,) * 81
        cell = Cell(20)

        # ACT
        is_puzzle_digit = analysis.is_puzzle_digit(cell)

        # ASSERT
        assert not is_puzzle_digit

    def test_is_complete_returns_false_when_grid_is_not_full(self, analysis, state):
        # ARRANGE
        state.filled_cells = MagicMock()
        state.filled_cells.__len__.return_value = 80

        # ACT
        complete = analysis.is_complete()

        # ASSERT
        assert not complete

    def test_is_complete_returns_false_for_duplicate_in_row(self, analysis, state):
        # ARRANGE
        state.filled_cells = Cells.with_all()
        # fmt: off
        state.digits = [
            5, 3, 4, 6, 7, 3, 9, 1, 2,
            6, 7, 2, 1, 9, 5, 3, 4, 8,
            1, 9, 8, 8, 4, 2, 5, 6, 7,
            8, 5, 9, 7, 6, 1, 4, 2, 3,
            4, 2, 6, 3, 5, 8, 7, 9, 1,
            7, 1, 3, 9, 2, 4, 8, 5, 6,
            9, 6, 1, 5, 3, 7, 2, 8, 4,
            2, 8, 7, 4, 1, 9, 6, 3, 5,
            3, 4, 5, 2, 8, 6, 1, 7, 9
        ]
        # fmt: on

        # ACT
        complete = analysis.is_complete()

        # ASSERT
        assert not complete

    def test_is_complete_returns_false_for_duplicate_in_col(self, analysis, state):
        # ARRANGE
        state.filled_cells = Cells.with_all()

        # fmt: off
        state.digits = [
            5, 3, 4, 6, 7, 8, 9, 1, 2,
            6, 7, 2, 1, 9, 5, 3, 4, 8,
            1, 9, 8, 3, 4, 2, 5, 6, 7,
            5, 8, 9, 7, 6, 1, 4, 2, 3,
            4, 2, 6, 8, 5, 3, 7, 9, 1,
            7, 1, 3, 9, 2, 4, 8, 5, 6,
            9, 6, 1, 5, 3, 7, 2, 8, 4,
            2, 8, 7, 4, 1, 9, 6, 3, 5,
            3, 4, 5, 2, 8, 6, 1, 7, 9
        ]
        # fmt: on

        # ACT
        complete = analysis.is_complete()

        # ASSERT
        assert not complete

    def test_is_complete_returns_false_for_duplicate_in_box(self, analysis, state):
        # ARRANGE
        state.filled_cells = Cells.with_all()

        # fmt: off
        state.digits = [
            5, 3, 4, 6, 7, 8, 9, 1, 2,
            6, 5, 2, 7, 9, 1, 3, 4, 8,
            1, 9, 8, 3, 4, 2, 5, 6, 7,
            8, 7, 9, 1, 6, 5, 4, 2, 3,
            4, 2, 6, 8, 5, 3, 7, 9, 1,
            7, 1, 3, 9, 2, 4, 8, 5, 6,
            9, 6, 1, 5, 3, 7, 2, 8, 4,
            2, 8, 7, 4, 1, 9, 6, 3, 5,
            3, 4, 5, 2, 8, 6, 1, 7, 9
        ]
        # fmt: on

        # ACT
        complete = analysis.is_complete()

        # ASSERT
        assert not complete

    def test_is_complete_is_true_for_a_valid_grid(self, analysis, state):
        # ARRANGE
        state.filled_cells = Cells.with_all()

        # fmt: off
        state.digits = [
        5, 3, 4, 6, 7, 8, 9, 1, 2,
        6, 7, 2, 1, 9, 5, 3, 4, 8,
        1, 9, 8, 3, 4, 2, 5, 6, 7,
        8, 5, 9, 7, 6, 1, 4, 2, 3,
        4, 2, 6, 8, 5, 3, 7, 9, 1,
        7, 1, 3, 9, 2, 4, 8, 5, 6,
        9, 6, 1, 5, 3, 7, 2, 8, 4,
        2, 8, 7, 4, 1, 9, 6, 3, 5,
        3, 4, 5, 2, 8, 6, 1, 7, 9
        ]
        # fmt: on

        # ACT
        complete = analysis.is_complete()

        # ASSERT
        assert complete

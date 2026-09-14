from unittest.mock import MagicMock, Mock, patch

import pytest

from sudoku_strategy.grid import Cell, CellCandidates, CellGroups, Cells, GridState
from sudoku_strategy.grid.analysis import GridAnalysis


class TestGridAnalysis:
    @pytest.fixture
    def state(self):
        state = Mock(GridState)

        state.digits = [None] * 81
        state.puzzle_digits = [None] * 81
        state.cell_candidates = [MagicMock(CellCandidates) for _ in range(81)]
        state.value_candidates = {digit: MagicMock(Cells) for digit in range(1, 10)}
        state.filled_cells = MagicMock(Cells)

        return state

    @pytest.fixture
    def cell_groups(self):
        return MagicMock(CellGroups)

    @pytest.fixture
    def analysis(self, state, cell_groups):
        return GridAnalysis(state, cell_groups)

    def test_get_cells_with_candidate_gets_intersection_of_given_cells_with_cells_with_candidate(
        self,
        analysis,
        state,
    ):
        # ARRANGE
        cells_in = {1, 2, 3}
        digit = 4
        state.value_candidates[digit] = {2, 3, 4}

        # ACT
        cells = analysis.get_cells_with_candidate(cells_in, digit)

        # ASSERT
        assert cells == {2, 3}

    def test_count_cells_with_candidate_gets_length_of_candidates(self, analysis):
        # ARRANGE
        cells_with_candidate = MagicMock(Cells)
        cells_with_candidate.__len__.return_value = 44

        with patch.object(
            analysis,
            "get_cells_with_candidate",
            return_value=cells_with_candidate,
        ):
            # ACT
            length = analysis.count_cells_with_candidate(Mock(Cells), 2)

        # ASSERT
        assert length == 44

    def test_get_candidates_for_cell_gets_candidates_for_the_cell(
        self,
        analysis,
        state,
    ):
        # ARRANGE
        cell = Mock(Cell, index=17)
        expected_candidates = state.cell_candidates[cell.index]

        # ACT
        candidates = analysis.get_candidates_for_cell(cell)

        # ASSERT
        assert candidates is expected_candidates

    def test_count_candidates_in_cell_gets_length_of_candidates_in_cell(self, analysis):
        # ARRANGE
        cell_candidates = MagicMock(CellCandidates)
        cell_candidates.__len__.return_value = 7

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
        cell = Mock(Cell, index=15)
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
        cell = Mock(Cell, index=26)
        state.cell_candidates[cell.index] = {3, 5, 7, 8}

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
        cell = Mock(Cell, index=26)
        state.cell_candidates[cell.index] = {3, 5, 7, 8}

        # ACT
        contained = analysis.cell_has_candidate(cell, digit)

        # ASSERT
        assert not contained

    def test_is_puzzle_digit_returns_true_for_a_puzzle_digit(self, analysis, state):
        # ARRANGE
        state.puzzle_digits = (0,) * 20 + (1,) + (0,) * 60
        cell = Mock(Cell, index=20)

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
        cell = Mock(Cell, index=20)

        # ACT
        is_puzzle_digit = analysis.is_puzzle_digit(cell)

        # ASSERT
        assert not is_puzzle_digit

    def test_is_complete_returns_false_when_grid_is_not_full(self, analysis, state):
        # ARRANGE
        state.filled_cells.__len__.return_value = 80

        # ACT
        complete = analysis.is_complete()

        # ASSERT
        assert not complete

    def test_is_complete_returns_false_for_duplicate_in_row(self, analysis, state):
        # ARRANGE
        state.filled_cells.__len__.return_value = 81

        digits = [1, 2, 3, 3, 5, 6, 7, 8, 9]
        analysis.get_digit_in_cell = Mock()
        analysis.get_digit_in_cell.side_effect = digits

        cells = [
            Mock(Cell, row=1, col=0, box=0),
            Mock(Cell, row=1, col=1, box=0),
            Mock(Cell, row=1, col=2, box=0),
            Mock(Cell, row=1, col=3, box=1),
            Mock(Cell, row=1, col=4, box=1),
            Mock(Cell, row=1, col=5, box=1),
            Mock(Cell, row=1, col=6, box=2),
            Mock(Cell, row=1, col=7, box=2),
            Mock(Cell, row=1, col=8, box=2),
        ]
        analysis.cell_groups.cells = Mock(Cells)
        analysis.cell_groups.cells.return_value = cells

        # ACT
        complete = analysis.is_complete()

        # ASSERT
        assert not complete

    def test_is_complete_returns_false_for_duplicate_in_col(self, analysis, state):
        # ARRANGE
        state.filled_cells.__len__.return_value = 81

        digits = [1, 2, 3, 4, 5, 6, 2, 8, 9]
        analysis.get_digit_in_cell = Mock()
        analysis.get_digit_in_cell.side_effect = digits

        cells = [
            Mock(Cell, row=0, col=5, box=1),
            Mock(Cell, row=1, col=5, box=1),
            Mock(Cell, row=2, col=5, box=1),
            Mock(Cell, row=3, col=5, box=4),
            Mock(Cell, row=4, col=5, box=4),
            Mock(Cell, row=5, col=5, box=4),
            Mock(Cell, row=6, col=5, box=7),
            Mock(Cell, row=7, col=5, box=7),
            Mock(Cell, row=8, col=5, box=7),
        ]
        analysis.cell_groups.cells = Mock(Cells)
        analysis.cell_groups.cells.return_value = cells

        # ACT
        complete = analysis.is_complete()

        # ASSERT
        assert not complete

    def test_is_complete_returns_false_for_duplicate_in_box(self, analysis, state):
        # ARRANGE
        state.filled_cells.__len__.return_value = 81

        digits = [1, 2, 3, 9, 5, 6, 7, 8, 9]
        analysis.get_digit_in_cell = Mock()
        analysis.get_digit_in_cell.side_effect = digits

        cells = [
            Mock(Cell, row=0, col=0, box=0),
            Mock(Cell, row=0, col=1, box=0),
            Mock(Cell, row=0, col=2, box=0),
            Mock(Cell, row=1, col=0, box=0),
            Mock(Cell, row=1, col=1, box=0),
            Mock(Cell, row=1, col=2, box=0),
            Mock(Cell, row=2, col=0, box=0),
            Mock(Cell, row=2, col=1, box=0),
            Mock(Cell, row=2, col=2, box=0),
        ]
        analysis.cell_groups.cells = Mock(Cells)
        analysis.cell_groups.cells.return_value = cells

        # ACT
        complete = analysis.is_complete()

        # ASSERT
        assert not complete

    def test_is_complete_is_true_for_a_valid_grid(self, analysis, state):
        # ARRANGE
        state.filled_cells.__len__.return_value = 81

        # fmt: off
        digits = [
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
        analysis.get_digit_in_cell = Mock()
        analysis.get_digit_in_cell.side_effect = digits

        cells = [
            Mock(Cell, row=i // 9, col=i % 9, box=(i // 27) * 3 + (i % 9) // 3)
            for i in range(81)
        ]
        analysis.cell_groups.cells = Mock(Cells)
        analysis.cell_groups.cells.return_value = cells

        # ACT
        complete = analysis.is_complete()

        # ASSERT
        assert complete

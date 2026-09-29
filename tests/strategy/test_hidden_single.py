import pytest

from sudoku_strategy.grid import Cell, CellCandidates, Cells
from sudoku_strategy.strategy.hidden_single import HiddenSingleStrategy


class TestHiddenSingleStrategy:
    @pytest.fixture
    def strategy(self):
        return HiddenSingleStrategy()

    def test_finds_hidden_single(self, analysis, state, strategy):
        # ARRANGE
        state.cell_candidates = [
            CellCandidates.from_digits([1, 2, 3, 4, 6, 7, 8, 9]) for _ in range(81)
        ]
        state.value_candidates = [Cells.with_all() for _ in range(10)]

        hidden_single = Cell.from_position(3, 1)
        state.cell_candidates[hidden_single.index] = CellCandidates.from_digits([5])
        state.value_candidates[5] = Cells() + hidden_single

        # ACT
        deduction = strategy.find(analysis)

        # ASSERT
        assert deduction is not None
        assert deduction.strategy == "Hidden Single"
        assert deduction.assignment is not None
        assert deduction.assignment.cell == hidden_single
        assert deduction.assignment.digit == 5
        assert deduction.explanation == ("5 is a hidden single in cell R4C2")

    def test_returns_none_when_no_hidden_single(self, analysis, state, strategy):
        # ARRANGE
        state.cell_candidates = [
            CellCandidates.from_digits([1, 2, 3, 4, 5, 6, 7, 8, 9]) for _ in range(81)
        ]
        state.value_candidates = [Cells.with_all() for _ in range(10)]

        # ACT
        result = strategy.find(analysis)

        # ASSERT
        assert result is None

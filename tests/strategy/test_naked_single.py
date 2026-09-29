import pytest

from sudoku_strategy.grid import Cell, CellCandidates
from sudoku_strategy.strategy.naked_single import NakedSingleStrategy


class TestNakedSingleStrategy:
    @pytest.fixture
    def strategy(self):
        return NakedSingleStrategy()

    def test_finds_naked_single(self, analysis, state, strategy):
        # ARRANGE
        cell = Cell(33)
        state.cell_candidates[cell.index] = CellCandidates.from_digits([5])

        # ACT
        deduction = strategy.find(analysis)

        # ASSERT
        assert deduction is not None
        assert deduction.strategy == "Naked Single"
        assert deduction.assignment is not None
        assert deduction.assignment.cell == cell
        assert deduction.assignment.digit == 5
        assert deduction.explanation == "Cell R4C7 is a naked single with value 5."

    def test_returns_none_when_no_naked_single(self, analysis, state, strategy):
        # ARRANGE
        cells = (
            Cell(0),
            Cell(1),
            Cell(2),
        )

        state.cell_candidates[cells[0].index] = CellCandidates(0b110000000)
        state.cell_candidates[cells[1].index] = CellCandidates(0b111000000)
        state.cell_candidates[cells[2].index] = CellCandidates(0b111100000)

        # ACT
        result = strategy.find(analysis)

        # ASSERT
        assert result is None

    def test_returns_first_naked_single(self, analysis, state, strategy):
        # ARRANGE
        first = Cell(0)
        state.cell_candidates[first.index] = CellCandidates.from_digits([2, 7])

        second = Cell(41)
        state.cell_candidates[second.index] = CellCandidates.from_digits([7])

        # ACT
        deduction = strategy.find(analysis)

        # ASSERT
        assert deduction is not None
        assert deduction.assignment is not None
        assert deduction.assignment.cell == second
        assert deduction.assignment.digit == 7

    def test_stops_after_finding_naked_single(self, analysis, state, strategy):
        # ARRANGE
        first = Cell(0)
        state.cell_candidates[first.index] = CellCandidates.from_digits([1, 2])

        second = Cell(1)
        state.cell_candidates[second.index] = CellCandidates.from_digits([3])

        third = Cell(2)
        state.cell_candidates[third.index] = CellCandidates.from_digits([4])

        # ACT
        deduction = strategy.find(analysis)

        # ASSERT
        assert deduction.assignment.digit == 3
        assert deduction.assignment.cell == second

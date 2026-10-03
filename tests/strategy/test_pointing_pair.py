from unittest.mock import Mock

import pytest

from sudoku_strategy.grid import Cell, CellCandidates
from sudoku_strategy.strategy.deduction import CellDigit
from sudoku_strategy.strategy.pointing_pair import PointingPair, PointingPairStrategy


class TestPointingPairStrategy:
    @pytest.fixture
    def strategy(self):
        return PointingPairStrategy()

    def test_finds_pointing_pair_in_row(self, analysis, state, strategy):
        # ARRANGE
        digit = 1

        first = Cell(0)
        state.cell_candidates[first.index] = CellCandidates.empty() + digit
        state.value_candidates[digit] += first

        second = Cell(1)
        state.cell_candidates[second.index] = CellCandidates.empty() + digit
        state.value_candidates[digit] += second

        third = Cell(2)
        state.cell_candidates[third.index] = CellCandidates.empty() + digit
        state.value_candidates[digit] += third

        fourth = Cell(4)
        state.cell_candidates[fourth.index] = CellCandidates.empty() + digit
        state.value_candidates[digit] += fourth

        # ACT
        deduction = strategy.find(analysis)

        # ASSERT
        assert deduction is not None
        assert deduction.strategy == "Pointing Pair"
        assert deduction.eliminations == [CellDigit(fourth, 1)]
        assert deduction.explanation == (
            "Candidates for 1 in box 0 allow for eliminations in R1C5."
        )

    def test_finds_pointing_pair_in_column(self, analysis, state, strategy):
        # ARRANGE
        digit = 1

        first = Cell.from_position(0, 0)
        state.cell_candidates[first.index] = CellCandidates.empty() + digit
        state.value_candidates[digit] += first

        second = Cell.from_position(1, 0)
        state.cell_candidates[second.index] = CellCandidates.empty() + digit
        state.value_candidates[digit] += second

        third = Cell.from_position(3, 0)
        state.cell_candidates[third.index] = CellCandidates.empty() + digit
        state.value_candidates[digit] += third

        # ACT
        deduction = strategy.find(analysis)

        # ASSERT
        assert deduction is not None
        assert deduction.strategy == "Pointing Pair"
        assert deduction.eliminations == [CellDigit(third, 1)]
        assert deduction.explanation == (
            "Candidates for 1 in box 0 allow for eliminations in R4C1."
        )

    def test_find_returns_none_when_no_pointing_pair(self, analysis, strategy):
        # ARRANGE
        strategy._find_pointing_pairs = Mock(return_value=iter([]))

        # ACT
        result = strategy.find(analysis)

        # ASSERT
        assert result is None

    def test_returns_none_when_pointing_pair_has_no_eliminations(
        self, analysis, strategy
    ):
        # ARRANGE
        pointing_pair = PointingPair(5, 2, analysis.cell_groups.row(7))
        strategy._find_pointing_pairs = Mock(return_value=[pointing_pair])

        # ACT
        result = strategy.find(analysis)

        # ASSERT
        assert result is None

    def test_skips_candidate_when_more_than_three_cells_have_it(
        self, analysis, state, strategy
    ):
        # ARRANGE
        digit = 2
        cells = (
            Cell.from_position(row=0, col=0),
            Cell.from_position(row=0, col=1),
            Cell.from_position(row=0, col=2),
            Cell.from_position(row=1, col=0),
        )

        for cell in cells:
            state.cell_candidates[cell.index] += digit
            state.value_candidates[digit] += cell

        # ACT
        result = strategy.find(analysis)

        # ASSERT
        assert result is None

    def test_find_doesnt_give_pointing_pair_without_elimination(
        self,
        analysis,
        state,
        strategy,
    ):
        # ARRANGE
        digit1 = 3
        for col in (0, 2):
            cell = Cell.from_position(0, col)
            state.cell_candidates[cell.index] += digit1
            state.value_candidates[digit1] += cell

        digit2 = 6
        for col in (0, 1, 5):
            cell = Cell.from_position(1, col)
            state.cell_candidates[cell.index] += digit2
            state.value_candidates[digit2] += cell

        # ACT
        deduction = strategy.find(analysis)

        # ASSERT
        assert len(deduction.eliminations) == 1
        assert deduction.eliminations[0].digit == digit2
        assert deduction.eliminations[0].cell.col == 5

    def test_get_eliminations_ignores_cells_in_pointing_pair_box(
        self, analysis, state, strategy
    ):
        # ARRANGE
        digit = 5
        cols = (0, 1, 3)
        row = 0
        for col in cols:
            cell = Cell.from_position(row, col)
            state.cell_candidates[cell.index] += digit
            state.value_candidates[digit] += cell

        pointing_pair = PointingPair(
            digit=digit,
            box=0,
            line=analysis.cell_groups.row(0),
        )

        # ACT
        eliminations = strategy._get_eliminations(
            analysis,
            pointing_pair,
        )

        # ASSERT
        assert len(eliminations) == 1
        assert eliminations[0].digit == digit
        assert eliminations[0].cell.row == 0
        assert eliminations[0].cell.box != 0

    def test_get_eliminations_only_returns_cells_with_candidate(
        self,
        analysis,
        state,
        strategy,
    ):
        # ARRANGE
        digit = 6
        cols = (0, 1, 3, 7)
        row = 0
        cells = [Cell.from_position(row, col) for col in cols]
        for cell in cells:
            state.cell_candidates[cell.index] += digit
            state.value_candidates[digit] += cell

        pointing_pair = PointingPair(
            digit=digit,
            box=0,
            line=analysis.cell_groups.row(0),
        )

        # ACT
        eliminations = strategy._get_eliminations(
            analysis,
            pointing_pair,
        )

        # ASSERT
        assert eliminations == [
            CellDigit(cells[2], digit),
            CellDigit(cells[3], digit),
        ]

    def test_get_eliminations_returns_empty_when_no_cells_have_candidate(
        self, analysis, state, strategy
    ):
        # ARRANGE
        digit = 3

        for i in range(9):
            state.cell_candidates[i] = CellCandidates.with_all() - digit

        pointing_pair = PointingPair(
            digit=digit,
            box=0,
            line=analysis.cell_groups.row(0),
        )

        # ACT
        eliminations = strategy._get_eliminations(
            analysis,
            pointing_pair,
        )

        # ASSERT
        assert eliminations == []

from unittest.mock import MagicMock, Mock

import pytest

from sudoku_strategy.grid import Cell
from sudoku_strategy.strategy.naked_single import NakedSingleStrategy


class TestNakedSingleStrategy:
    @pytest.fixture
    def strategy(self):
        return NakedSingleStrategy()

    def test_finds_naked_single(self, analysis, strategy):
        # ARRANGE
        cell = MagicMock(Cell, row=3, col=6)
        cell.configure_mock(**{"__str__.return_value": "R4C7"})

        analysis.cell_groups.empty_cells.return_value = [cell]
        analysis.count_candidates_in_cell.return_value = 1
        analysis.get_candidates_for_cell.return_value = (5,)

        # ACT
        deduction = strategy.find(analysis)

        # ASSERT
        assert deduction is not None
        assert deduction.strategy == "Naked Single"
        assert deduction.assignment is not None
        assert deduction.assignment.cell is cell
        assert deduction.assignment.digit == 5
        assert deduction.explanation == "Cell R4C7 is a naked single with value 5."

    def test_returns_none_when_no_naked_single(self, analysis, strategy):
        # ARRANGE
        cells = (
            Mock(Cell, row=0, col=0),
            Mock(Cell, row=0, col=1),
            Mock(Cell, row=0, col=2),
        )

        analysis.cell_groups.empty_cells.return_value = cells
        analysis.count_candidates_in_cell.side_effect = [2, 3, 4]

        # ACT
        result = strategy.find(analysis)

        # ASSERT
        assert result is None

    def test_returns_first_naked_single(self, analysis, strategy):
        # ARRANGE
        first = Mock(Cell, row=0, col=0)
        second = Mock(Cell, row=4, col=5)

        analysis.cell_groups.empty_cells.return_value = (first, second)
        analysis.count_candidates_in_cell.side_effect = [2, 1]
        analysis.get_candidates_for_cell.return_value = (7,)

        # ACT
        deduction = strategy.find(analysis)

        # ASSERT
        assert deduction is not None
        assert deduction.assignment is not None
        assert deduction.assignment.cell is second
        assert deduction.assignment.digit == 7

    def test_stops_after_finding_naked_single(self, analysis, strategy):
        # ARRANGE
        first = Mock(Cell, row=0, col=0)
        second = Mock(Cell, row=0, col=1)
        third = Mock(Cell, row=0, col=2)

        analysis.cell_groups.empty_cells.return_value = (first, second, third)
        analysis.count_candidates_in_cell.side_effect = [2, 1, 1]
        analysis.get_candidates_for_cell.return_value = (4,)

        # ACT
        strategy.find(analysis)

        # ASSERT
        assert analysis.count_candidates_in_cell.call_count == 2

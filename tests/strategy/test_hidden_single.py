from unittest.mock import MagicMock, Mock

import pytest

from sudoku_strategy.grid import Cell
from sudoku_strategy.strategy.hidden_single import HiddenSingleStrategy


class TestHiddenSingleStrategy:
    @pytest.fixture
    def strategy(self):
        return HiddenSingleStrategy()

    def test_finds_hidden_single(self, analysis, strategy):
        # ARRANGE
        hidden_single = MagicMock(Cell, row=3, col=2)
        hidden_single.configure_mock(**{"__str__.return_value": "R4C2"})

        cells = [
            Mock(Cell, row=3, col=0),
            hidden_single,
            Mock(Cell, row=3, col=2),
        ]

        analysis.cell_groups.units.return_value = (cells,)

        analysis.get_cells_with_candidate.side_effect = [
            (cells[0], cells[1]),  # 1 can go in two cells
            (cells[0], cells[1]),  # 2 can go in two cells
            (cells[1],),  # 3 can only go in cells[1]
        ]

        # ACT
        deduction = strategy.find(analysis)

        # ASSERT
        assert deduction is not None
        assert deduction.strategy == "Hidden Single"
        assert deduction.assignment is not None
        assert deduction.assignment.cell is cells[1]
        assert deduction.assignment.digit == 3
        assert deduction.explanation == ("3 is a hidden single in cell R4C2")

    def test_returns_none_when_no_hidden_single(self, analysis, strategy):
        # ARRANGE
        cells = (
            Mock(Cell, row=0, col=0),
            Mock(Cell, row=0, col=1),
        )

        analysis.cell_groups.units.return_value = (cells,)

        analysis.get_cells_with_candidate.side_effect = [
            (cells[0], cells[1]),
        ] * 9

        # ACT
        result = strategy.find(analysis)

        # ASSERT
        assert result is None

    def test_returns_first_hidden_single(self, analysis, strategy):
        # ARRANGE
        first = Mock(Cell, row=0, col=0)
        second = Mock(Cell, row=0, col=1)

        cells = [first, second]

        analysis.cell_groups.units.return_value = (cells,)

        analysis.get_cells_with_candidate.side_effect = [
            (first,),  # 1 is a hidden single
            (second,),  # 2 is also a hidden single
        ]

        # ACT
        deduction = strategy.find(analysis)

        # ASSERT
        assert deduction is not None
        assert deduction.assignment is not None
        assert deduction.assignment.cell is first
        assert deduction.assignment.digit == 1

    def test_stops_after_finding_hidden_single(self, analysis, strategy):
        # ARRANGE
        first = Mock(Cell, row=0, col=0)
        second = Mock(Cell, row=0, col=1)
        third = Mock(Cell, row=0, col=2)

        cells = [first, second, third]

        analysis.cell_groups.units.return_value = (cells,)

        analysis.get_cells_with_candidate.side_effect = [
            (first,),  # 1 is a hidden single
            (second,),  # 2 should not be checked
            (third,),  # 3 should not be checked
        ]

        # ACT
        strategy.find(analysis)

        # ASSERT
        assert analysis.get_cells_with_candidate.call_count == 1

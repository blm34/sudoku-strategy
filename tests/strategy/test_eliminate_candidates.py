from unittest.mock import Mock

import pytest

from sudoku_strategy.grid import Cell
from sudoku_strategy.strategy.deduction import CellDigit
from sudoku_strategy.strategy.eliminate_candidates import EliminateCandidatesStrategy


class TestEliminateCandidatesStrategy:
    @pytest.fixture
    def strategy(self):
        return EliminateCandidatesStrategy()

    def test_finds_eliminatable_candidate(self, analysis, strategy):
        # ARRANGE
        filled_cell = Mock(Cell, row=0, col=0)
        peer = Mock(Cell, row=0, col=1)

        analysis.cell_groups.filled_cells.return_value = [filled_cell]
        analysis.get_digit_in_cell.return_value = 5
        analysis.cell_groups.peers.return_value = [peer]
        analysis.get_cells_with_candidate.return_value = [peer]

        # ACT
        deduction = strategy.find(analysis)

        # ASSERT
        assert deduction is not None
        assert deduction.strategy == "Candidate Elimination"
        assert deduction.eliminations == [CellDigit(peer, 5)]
        assert deduction.explanation == (
            "The given candidates are already accounted for in a given unit"
        )

    def test_returns_none_when_no_candidates_can_be_eliminated(
        self, analysis, strategy
    ):
        # ARRANGE
        filled_cell = Mock(Cell, row=0, col=0)
        peer = Mock(Cell, row=0, col=1)

        analysis.cell_groups.filled_cells.return_value = [filled_cell]
        analysis.get_digit_in_cell.return_value = 5
        analysis.cell_groups.peers.return_value = [peer]
        analysis.get_cells_with_candidate.return_value = []

        # ACT
        result = strategy.find(analysis)

        # ASSERT
        assert result is None

    def test_finds_multiple_eliminatable_candidates(self, analysis, strategy):
        # ARRANGE
        filled_cell = Mock(Cell, row=0, col=0)
        first_peer = Mock(Cell, row=0, col=1)
        second_peer = Mock(Cell, row=1, col=0)

        analysis.cell_groups.filled_cells.return_value = [filled_cell]
        analysis.get_digit_in_cell.return_value = 5
        analysis.cell_groups.peers.return_value = [first_peer, second_peer]
        analysis.get_cells_with_candidate.return_value = [
            first_peer,
            second_peer,
        ]

        # ACT
        deduction = strategy.find(analysis)

        # ASSERT
        assert deduction is not None
        assert deduction.eliminations == [
            CellDigit(first_peer, 5),
            CellDigit(second_peer, 5),
        ]

    def test_finds_eliminations_from_multiple_filled_cells(self, analysis, strategy):
        # ARRANGE
        first_filled = Mock(Cell, row=0, col=0)
        second_filled = Mock(Cell, row=1, col=1)

        first_peer = Mock(Cell, row=0, col=1)
        second_peer = Mock(Cell, row=1, col=2)

        analysis.cell_groups.filled_cells.return_value = (
            first_filled,
            second_filled,
        )

        analysis.get_digit_in_cell.side_effect = [5, 7]

        analysis.cell_groups.peers.side_effect = [
            [first_peer],
            [second_peer],
        ]

        analysis.get_cells_with_candidate.side_effect = [
            [first_peer],
            [second_peer],
        ]

        # ACT
        deduction = strategy.find(analysis)

        # ASSERT
        assert deduction is not None
        assert deduction.eliminations == [
            CellDigit(first_peer, 5),
            CellDigit(second_peer, 7),
        ]

    def test_checks_all_filled_cells(self, analysis, strategy):
        # ARRANGE
        first = Mock(Cell, row=0, col=0)
        second = Mock(Cell, row=0, col=1)
        third = Mock(Cell, row=0, col=2)

        analysis.cell_groups.filled_cells.return_value = (first, second, third)

        analysis.get_digit_in_cell.side_effect = [5, 6, 7]
        analysis.cell_groups.peers.side_effect = [
            [],
            [],
            [],
        ]
        analysis.get_cells_with_candidate.return_value = []

        # ACT
        result = strategy.find(analysis)

        # ASSERT
        assert result is None
        assert analysis.get_digit_in_cell.call_count == 3
        assert analysis.cell_groups.peers.call_count == 3
        assert analysis.get_cells_with_candidate.call_count == 3

    def test_gets_candidates_for_filled_cell_digit_from_its_peers(
        self, analysis, strategy
    ):
        # ARRANGE
        filled_cell = Mock(Cell, row=3, col=6)
        peers = (
            Mock(Cell, row=3, col=0),
            Mock(Cell, row=3, col=1),
        )

        analysis.cell_groups.filled_cells.return_value = [filled_cell]
        analysis.get_digit_in_cell.return_value = 5
        analysis.cell_groups.peers.return_value = peers
        analysis.get_cells_with_candidate.return_value = []

        # ACT
        strategy.find(analysis)

        # ASSERT
        analysis.get_digit_in_cell.assert_called_once_with(filled_cell)
        analysis.cell_groups.peers.assert_called_once_with(filled_cell)
        analysis.get_cells_with_candidate.assert_called_once_with(peers, 5)

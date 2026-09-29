import pytest

from sudoku_strategy.grid import Cell
from sudoku_strategy.strategy.deduction import CellDigit
from sudoku_strategy.strategy.eliminate_candidates import EliminateCandidatesStrategy


class TestEliminateCandidatesStrategy:
    @pytest.fixture
    def strategy(self):
        return EliminateCandidatesStrategy()

    def test_finds_eliminatable_candidate(self, analysis, state, strategy):
        # ARRANGE
        digit = 5
        filled_cell = Cell(0)
        state.digits[filled_cell.index] = digit
        state.filled_cells += filled_cell

        peer = Cell(1)
        state.cell_candidates[peer.index] += digit
        state.value_candidates[digit] += peer

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
        self, analysis, state, strategy
    ):
        # ARRANGE
        digit = 5
        filled_cell = Cell(0)
        state.digits[filled_cell.index] = digit
        state.filled_cells += filled_cell

        # ACT
        result = strategy.find(analysis)

        # ASSERT
        assert result is None

    def test_finds_multiple_eliminatable_candidates(self, analysis, state, strategy):
        # ARRANGE
        digit = 5
        filled_cell = Cell(0)
        state.digits[filled_cell.index] = digit
        state.filled_cells += filled_cell

        peers = (Cell(1), Cell(9))
        for peer in peers:
            state.cell_candidates[peer.index] += digit
            state.value_candidates[digit] += peer

        # ACT
        deduction = strategy.find(analysis)

        # ASSERT
        assert deduction is not None
        assert deduction.eliminations == [
            CellDigit(peers[0], digit),
            CellDigit(peers[1], digit),
        ]

    def test_finds_eliminations_from_multiple_filled_cells(
        self, analysis, state, strategy
    ):
        # ARRANGE
        filled_cell_1 = Cell(0)
        state.digits[filled_cell_1.index] = 5
        state.filled_cells += filled_cell_1

        filled_cell_2 = Cell(10)
        state.digits[filled_cell_2.index] = 7
        state.filled_cells += filled_cell_2

        peer_1 = Cell(1)
        state.cell_candidates[peer_1.index] += 5
        state.value_candidates[5] += peer_1

        peer_2 = Cell(2)
        state.cell_candidates[peer_2.index] += 7
        state.value_candidates[7] += peer_2

        # ACT
        deduction = strategy.find(analysis)

        # ASSERT
        assert deduction is not None
        assert deduction.eliminations == [
            CellDigit(peer_1, 5),
            CellDigit(peer_2, 7),
        ]

    def test_gets_candidates_for_filled_cell_digit_from_its_peers(
        self, analysis, state, strategy
    ):
        # ARRANGE
        digit = 6

        filled_cell = Cell(33)
        state.digits[filled_cell.index] = digit
        state.filled_cells += filled_cell

        peer = Cell(27)
        state.cell_candidates[peer.index] += digit
        state.value_candidates[digit] += peer

        not_peer = Cell(2)
        state.cell_candidates[not_peer.index] += digit
        state.value_candidates[digit] += not_peer

        # ACT
        deduction = strategy.find(analysis)

        # ASSERT
        assert len(deduction.eliminations) == 1
        assert deduction.eliminations[0].cell == peer
        assert deduction.eliminations[0].digit == digit

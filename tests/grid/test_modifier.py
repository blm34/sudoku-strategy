from unittest.mock import Mock, patch

import pytest

from sudoku_strategy.grid import Cell, CellCandidates, CellGroups, Cells, GridState
from sudoku_strategy.grid.modifier import GridModifier
from sudoku_strategy.strategy.deduction import CellDigit, Deduction


class TestGridModifier:
    @pytest.fixture
    def state(self):
        return GridState.create_empty()

    @pytest.fixture
    def cell_groups(self, state):
        return CellGroups(state)

    @pytest.fixture
    def modifier(self, state, cell_groups):
        return GridModifier(state, cell_groups)

    def test_set_digit_writes_to_digit(self, modifier, state):
        # ARRANGE
        cell_index = 42
        digit = 7

        # ACT
        modifier._set_digit(digit, cell_index)

        # ASSERT
        assert state.digits[cell_index] == digit

    def test_add_cell_to_filled_cells_updates_filled_cells(self, modifier, state):
        # ARRANGE
        cell = Cell(0)

        # ACT
        modifier._add_cell_to_filled_cells(cell)

        # ASSERT
        assert cell in state.filled_cells

    def test_clear_candidates_in_cell_updates_cell_candidates(self, modifier, state):
        # ARRANGE
        cell = Cell(42)
        cell_candidates = CellCandidates(0b111111111)

        state.cell_candidates[cell.index] = cell_candidates

        # ACT
        modifier._clear_candidates_in_cell(cell)

        # ASSERT
        assert len(state.cell_candidates[cell.index]) == 0

    def test_clear_candidates_in_cell_updates_value_candidates(self, modifier, state):
        # ARRANGE
        cell = Cell(42)
        state.cell_candidates[cell.index] = CellCandidates(0b100010010)
        state.value_candidates[2] = Cells(1 << cell.index)
        state.value_candidates[5] = Cells(1 << cell.index)
        state.value_candidates[9] = Cells(1 << cell.index)

        # ACT
        modifier._clear_candidates_in_cell(cell)

        # ASSERT
        assert cell not in state.value_candidates[2]
        assert cell not in state.value_candidates[5]
        assert cell not in state.value_candidates[9]

    def test_write_digit_updates_digits(self, modifier, state):
        # ARRANGE
        cell = Cell(42)

        # ACT
        modifier.write_digit(7, cell)

        # ASSERT
        assert state.digits[cell.index] == 7

    def test_write_digit_updates_filled_cells(self, modifier, state):
        # ARRANGE
        cell = Cell(42)

        # ACT
        modifier.write_digit(7, cell)

        # ASSERT
        assert cell in state.filled_cells

    def test_write_digit_updates_cell_candidates(self, modifier, state):
        # ARRANGE
        cell = Cell(42)
        state.cell_candidates[cell.index] = CellCandidates.with_all()

        # ACT
        modifier.write_digit(7, cell)

        # ASSERT
        assert len(state.cell_candidates[cell.index]) == 0

    def test_update_candidates_only_considers_peers_with_the_candidate(
        self,
        modifier,
        state,
        cell_groups,
    ):
        # ARRANGE
        cell = Cell(40)
        peer_with_candidate = Cell(41)
        candidate_but_not_peer = Cell(0)

        state.value_candidates[7] = Cells(
            (1 << peer_with_candidate.index) + (1 << candidate_but_not_peer.index)
        )

        with patch.object(modifier, "remove_candidate") as remove_candidate:
            # ACT
            modifier.update_candidates(7, cell)

            # ASSERT
            remove_candidate.assert_called_once_with(7, peer_with_candidate)

    def test_update_candidates_removes_candidate_from_all_resulting_cells(
        self, modifier, state, cell_groups
    ):
        # ARRANGE
        cell = Cell(5)
        peer = Cell(6)
        digit = 7
        state.cell_candidates[peer.index] = CellCandidates.from_digits([digit])
        state.value_candidates[digit] += peer

        # ACT
        modifier.update_candidates(7, cell)

        # ASSERT
        assert digit not in state.cell_candidates[peer.index]
        assert peer not in state.value_candidates[digit]

    def test_remove_candidate_updates_cell_candidates(self, modifier, state):
        # ARRANGE
        cell = Cell(42)
        digit = 7
        state.cell_candidates[cell.index] = CellCandidates.from_digits([digit])
        state.value_candidates[digit] += cell

        # ACT
        modifier.remove_candidate(digit, cell)

        # ASSERT
        assert digit not in state.cell_candidates[cell.index]

    def test_remove_candidate_updates_value_candidates(self, modifier, state):
        # ARRANGE
        cell = Cell(42)
        digit = 7
        state.cell_candidates[cell.index] = CellCandidates.from_digits([digit])
        state.value_candidates[digit] += cell

        # ACT
        modifier.remove_candidate(7, cell)

        # ASSERT
        assert cell not in state.value_candidates[digit]

    def test_remove_candidates_updates_cell_candidates(self, modifier, state):
        # ARRANGE
        cell = Cell(42)
        cell_candidates = CellCandidates.with_all()
        candidates_to_remove = [2, 5, 9]

        state.cell_candidates[cell.index] = cell_candidates
        for digit in range(1, 10):
            state.value_candidates[digit] += cell

        # ACT
        modifier.remove_candidates(candidates_to_remove, cell)

        # ASSERT
        for digit in candidates_to_remove:
            assert digit not in state.cell_candidates[cell.index]

    def test_remove_candidates_updates_value_candidates(self, modifier, state):
        # ARRANGE
        cell = Cell(42)
        cell_candidates = CellCandidates.with_all()
        candidates_to_remove = [2, 5, 9]

        state.cell_candidates[cell.index] = cell_candidates
        for digit in range(1, 10):
            state.value_candidates[digit] += cell

        # ACT
        modifier.remove_candidates(candidates_to_remove, cell)

        # ASSERT
        for digit in candidates_to_remove:
            assert cell not in state.value_candidates[digit]

    def test_add_candidate_updates_cell_candidates(self, modifier, state):
        # ARRANGE
        cell = Cell(42)

        # ACT
        modifier.add_candidate(2, cell)

        # ASSERT
        assert 2 in state.cell_candidates[cell.index]

    def test_add_candidate_updates_value_candidates(self, modifier, state):
        # ARRANGE
        cell = Cell(42)

        # ACT
        modifier.add_candidate(2, cell)

        # ASSERT
        assert cell in state.value_candidates[2]

    def test_add_candidates_updates_cell_candidates(self, modifier, state):
        # ARRANGE
        cell = Cell(24)
        candidates = [2, 5, 9]

        # ACT
        modifier.add_candidates(candidates, cell)

        # ASSERT
        for digit in candidates:
            assert digit in state.cell_candidates[cell.index]

    def test_add_candidates_updates_value_candidates(self, modifier, state):
        # ARRANGE
        cell = Cell(24)
        candidates = [2, 5, 9]

        # ACT
        modifier.add_candidates(candidates, cell)

        # ASSERT
        for digit in candidates:
            assert cell in state.value_candidates[digit]

    def test_apply_sets_digit_when_given(self, modifier, state):
        # ARRANGE
        cell = Cell(27)
        cell_digit = CellDigit(digit=7, cell=cell)
        deduction = Deduction(
            assignment=cell_digit,
            eliminations=[],
            strategy="",
            explanation="",
        )

        modifier.apply(deduction)

        # ASSERT
        assert state.digits[cell.index] == 7

    def test_apply_removes_candidates_when_eliminations_are_given(self, modifier):
        # ARRANGE
        elimination_1 = CellDigit(digit=2, cell=Cell(0))
        elimination_2 = CellDigit(digit=5, cell=Cell(1))

        deduction = Deduction(
            assignment=None,
            eliminations=[elimination_1, elimination_2],
            explanation="",
            strategy="",
        )

        with patch.object(modifier, "remove_candidate") as remove_candidate:
            # ACT
            modifier.apply(deduction)

            # ASSERT
            remove_candidate.assert_any_call(elimination_1.digit, elimination_1.cell)
            remove_candidate.assert_any_call(elimination_2.digit, elimination_2.cell)
            assert remove_candidate.call_count == 2

    def test_compute_candidates_initialises_filled_cells_as_empty(
        self,
        modifier,
        state,
        cell_groups,
    ):
        # ARRANGE
        cell = Cell(10)
        state.filled_cells += cell

        # ACT
        modifier.compute_candidates()

        # ASSERT
        assert len(state.cell_candidates[cell.index]) == 0

    def test_compute_candidates_initialises_empty_cells_with_all_candidates(
        self,
        modifier,
        state,
        cell_groups,
    ):
        # ARRANGE
        cell = Mock(Cell, index=10)

        # ACT
        modifier.compute_candidates()

        # ASSERT
        assert len(state.cell_candidates[cell.index]) == 9

    def test_compute_candidates_updates_candidates_for_filled_cells(
        self,
        modifier,
        state,
        cell_groups,
    ):
        # ARRANGE
        cell = Cell(10)
        digit = 3
        state.digits[cell.index] = digit
        state.filled_cells += cell

        with patch.object(modifier, "update_candidates") as update_candidates:
            # ACT
            modifier.compute_candidates()

        # ASSERT
        update_candidates.assert_called_once_with(digit, cell)

    def test_reset_restores_digits(self, modifier, state):
        # ARRANGE
        state.puzzle_digits = [1, 2, 3] + [None] * 78
        state.digits = [9] * 81

        # ACT
        modifier.reset()

        # ASSERT
        assert state.digits == state.puzzle_digits

    def test_reset_sets_all_cell_candidates_to_empty(self, modifier, state):
        # ARRANGE
        state.cell_candidates = [CellCandidates.with_all() for _ in range(81)]

        # ACT
        modifier.reset()

        # ASSERT
        assert all(len(candidates) == 0 for candidates in state.cell_candidates)

    def test_reset_sets_all_value_candidates_to_empty(self, modifier, state):
        # ARRANGE
        state.value_candidates = [Cells.with_all() for _ in range(10)]

        # ACT
        modifier.reset()

        # ASSERT
        assert all(len(cells) == 0 for cells in state.value_candidates[1:])

    def test_reset_updates_filled_cells(self, modifier, state):
        # ARRANGE
        state.fill_filled_cells = Mock()

        # ACT
        modifier.reset()

        # ASSERT
        state.fill_filled_cells.assert_called_once()

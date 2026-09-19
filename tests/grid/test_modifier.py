from unittest.mock import MagicMock, Mock, patch

import pytest

from sudoku_strategy.grid import Cell, CellCandidates, CellGroups, Cells, GridState
from sudoku_strategy.grid.modifier import GridModifier
from sudoku_strategy.strategy.deduction import CellDigit, Deduction


class TestGridModifier:
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
        cell = MagicMock(Cell)
        filled_cells = state.filled_cells

        # ACT
        modifier._add_cell_to_filled_cells(cell)

        # ASSERT
        filled_cells.__iadd__.assert_called_once_with(cell)

    def test_clear_candidates_in_cell_updates_cell_candidates(self, modifier, state):
        # ARRANGE
        cell = Mock(Cell, index=42)
        cell_candidates = MagicMock(CellCandidates)

        state.cell_candidates[cell.index] = cell_candidates

        # ACT
        modifier._clear_candidates_in_cell(cell)

        # ASSERT
        cell_candidates.remove_all.assert_called_once()

    def test_clear_candidates_in_cell_updates_value_candidates(self, modifier, state):
        # ARRANGE
        cell = Mock(Cell, index=42)
        cell_candidates = MagicMock(CellCandidates)

        value_candidates_2 = state.value_candidates[2]
        value_candidates_5 = state.value_candidates[5]
        value_candidates_9 = state.value_candidates[9]

        state.cell_candidates[cell.index] = cell_candidates
        cell_candidates.__iter__.return_value = iter([2, 5, 9])

        # ACT
        modifier._clear_candidates_in_cell(cell)

        # ASSERT
        value_candidates_2.__isub__.assert_called_once_with(cell)
        value_candidates_5.__isub__.assert_called_once_with(cell)
        value_candidates_9.__isub__.assert_called_once_with(cell)

    def test_write_digit_updates_digits(self, modifier, state):
        # ARRANGE
        cell = Mock(Cell, index=42)

        # ACT
        modifier.write_digit(7, cell)

        # ASSERT
        assert state.digits[cell.index] == 7

    def test_write_digit_updates_filled_cells(self, modifier):
        # ARRANGE
        cell = Mock(Cell, index=42)

        with patch.object(modifier, "_add_cell_to_filled_cells") as add_cell:
            # ACT
            modifier.write_digit(7, cell)

            # ASSERT
            add_cell.assert_called_once_with(cell)

    def test_write_digit_updates_cell_candidates(self, modifier):
        # ARRANGE
        cell = Mock(Cell, index=42)

        with patch.object(modifier, "_clear_candidates_in_cell") as clear_candidates:
            # ACT
            modifier.write_digit(7, cell)

            # ASSERT
            clear_candidates.assert_called_once_with(cell)

    def test_update_candidates_only_considers_peers_with_the_candidate(
        self, modifier, state, cell_groups
    ):
        # ARRANGE
        cell = Mock(Cell)
        peer_with_candidate = Mock(Cell)
        peer_without_candidate = Mock(Cell)
        candidate_but_not_peer = Mock(Cell)

        cell_groups.peers.return_value = {
            peer_with_candidate,
            peer_without_candidate,
        }
        state.value_candidates[7] = {
            peer_with_candidate,
            candidate_but_not_peer,
        }

        with patch.object(modifier, "remove_candidate") as remove_candidate:
            # ACT
            modifier.update_candidates(7, cell)

            # ASSERT
            remove_candidate.assert_called_once_with(7, peer_with_candidate)

    def test_update_candidates_removes_candidate_from_all_resulting_cells(
        self, modifier, state, cell_groups
    ):
        # ARRANGE
        cell = Mock(Cell)
        peer_1 = Mock(Cell)
        peer_2 = Mock(Cell)
        peer_3 = Mock(Cell)
        peers = {peer_1, peer_2, peer_3}

        cell_groups.peers.return_value = peers
        state.value_candidates[7] = peers

        with patch.object(modifier, "remove_candidate") as remove_candidate:
            # ACT
            modifier.update_candidates(7, cell)

            # ASSERT
            assert remove_candidate.call_count == 3
            remove_candidate.assert_any_call(7, peer_1)
            remove_candidate.assert_any_call(7, peer_2)
            remove_candidate.assert_any_call(7, peer_3)

    def test_remove_candidates_updates_cell_candidates(self, modifier, state):
        # ARRANGE
        cell = Mock(Cell, index=42)
        cell_candidates = MagicMock(CellCandidates)

        state.cell_candidates[cell.index] = cell_candidates

        # ACT
        modifier.remove_candidate(7, cell)

        # ASSERT
        cell_candidates.__isub__.assert_called_once_with(7)

    def test_remove_candidates_updates_value_candidates(self, modifier, state):
        # ARRANGE
        cell = Mock(Cell, index=42)
        value_candidates = MagicMock(Cells)

        state.value_candidates[7] = value_candidates

        # ACT
        modifier.remove_candidate(7, cell)

        # ASSERT
        value_candidates.__isub__.assert_called_once_with(cell)

    def test_add_candidate_updates_cell_candidates(self, modifier, state):
        # ARRANGE
        cell = Mock(Cell, index=42)
        cell_candidates = MagicMock(CellCandidates)
        candidates_to_remove = MagicMock(Cells)

        state.cell_candidates[cell.index] = cell_candidates

        with patch(
            "sudoku_strategy.grid.modifier.CellCandidates.from_digits",
            return_value=candidates_to_remove,
        ):
            # ACT
            modifier.remove_candidates([2, 5, 9], cell)

            # ASSERT
            candidates_to_remove.__invert__.assert_called_once()
            cell_candidates.__iand__.assert_called_once_with(
                candidates_to_remove.__invert__.return_value
            )

    def test_add_candidate_updates_value_candidates(self, modifier, state):
        # ARRANGE
        cell = Mock(Cell, index=42)
        candidates_to_add = MagicMock(CellCandidates)
        candidates_to_add.__iter__.return_value = iter([2])
        edited_value_candidates = state.value_candidates[2]

        with patch(
            "sudoku_strategy.grid.modifier.CellCandidates.from_digits",
            return_value=candidates_to_add,
        ):
            # ACT
            modifier.remove_candidates([2], cell)

            # ASSERT
            edited_value_candidates.__isub__.assert_called_once_with(cell)

    def test_add_candidates_updates_cell_candidates(self, modifier, state):
        # ARRANGE
        cell = Mock(Cell, index=24)
        cell_candidates = MagicMock(CellCandidates)
        candidates_to_add = MagicMock(CellCandidates)

        state.cell_candidates[cell.index] = cell_candidates

        with patch(
            "sudoku_strategy.grid.modifier.CellCandidates.from_digits",
            return_value=candidates_to_add,
        ):
            # ACT
            modifier.add_candidates([2, 5, 9], cell)

            # ASSERT
            cell_candidates.__ior__.assert_called_once_with(candidates_to_add)

    def test_add_candidates_updates_value_candidates(self, modifier, state):
        # ARRANGE
        cell = Mock(Cell, index=24)

        candidates_to_add = MagicMock(CellCandidates)
        candidates_to_add.__iter__.return_value = iter([2, 5, 9])

        value_candidates_2 = state.value_candidates[2]
        value_candidates_5 = state.value_candidates[5]
        value_candidates_9 = state.value_candidates[9]

        with patch(
            "sudoku_strategy.grid.modifier.CellCandidates.from_digits",
            return_value=candidates_to_add,
        ):
            # ACT
            modifier.add_candidates([2, 5, 9], cell)

            # ASSERT
            value_candidates_2.__iadd__.assert_called_once_with(cell)
            value_candidates_5.__iadd__.assert_called_once_with(cell)
            value_candidates_9.__iadd__.assert_called_once_with(cell)

    def test_apply_sets_digit_when_given(self, modifier):
        # ARRANGE
        cell_digit = Mock(CellDigit, digit=7, cell=Mock(Cell))
        deduction = Mock(Deduction, assignment=cell_digit, eliminations=[])

        with patch.object(modifier, "write_digit") as write_digit:
            # ACT
            modifier.apply(deduction)

            # ASSERT
            write_digit.assert_called_once_with(7, cell_digit.cell)

    def test_apply_removes_candidates_when_eliminations_are_given(self, modifier):
        # ARRANGE
        elimination_1 = Mock(CellDigit, digit=2, cell=Mock(Cell))
        elimination_2 = Mock(CellDigit, digit=5, cell=Mock(Cell))

        deduction = Mock(
            Deduction, assignment=None, eliminations=[elimination_1, elimination_2]
        )

        with patch.object(modifier, "remove_candidate") as remove_candidate:
            # ACT
            modifier.apply(deduction)

            # ASSERT
            remove_candidate.assert_any_call(elimination_1.digit, elimination_1.cell)
            remove_candidate.assert_any_call(elimination_2.digit, elimination_2.cell)
            assert remove_candidate.call_count == 2

    def test_compute_candidates_initialises_filled_cells_as_empty(
        self, modifier, state, cell_groups
    ):
        # ARRANGE
        cell = Mock(Cell, index=10)
        cell_groups.filled_cells.return_value = [cell]
        cell_groups.empty_cells.return_value = []

        empty_candidates = MagicMock(CellCandidates)

        with (
            patch(
                "sudoku_strategy.grid.modifier.CellCandidates.empty",
                return_value=empty_candidates,
            ),
            patch.object(modifier, "update_candidates"),
        ):
            # ACT
            modifier.compute_candidates()

        # ASSERT
        assert state.cell_candidates[cell.index] is empty_candidates

    def test_compute_candidates_initialises_empty_cells_with_all_candidates(
        self, modifier, state, cell_groups
    ):
        # ARRANGE
        cell = Mock(Cell, index=10)
        cell_groups.filled_cells.return_value = []
        cell_groups.empty_cells.return_value = [cell]

        all_candidates = MagicMock(CellCandidates)

        with patch(
            "sudoku_strategy.grid.modifier.CellCandidates.with_all",
            return_value=all_candidates,
        ):
            # ACT
            modifier.compute_candidates()

        # ASSERT
        assert state.cell_candidates[cell.index] is all_candidates

    def test_compute_candidates_updates_candidates_for_filled_cells(
        self, modifier, state, cell_groups
    ):
        # ARRANGE
        cell = Mock(Cell, index=10)
        state.digits[cell.index] = 3
        cell_groups.filled_cells.return_value = [cell]
        cell_groups.empty_cells.return_value = []

        with patch.object(modifier, "update_candidates") as update_candidates:
            # ACT
            modifier.compute_candidates()

        # ASSERT
        update_candidates.assert_called_once_with(3, cell)

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
        empty_candidates = MagicMock(CellCandidates)

        with patch(
            "sudoku_strategy.grid.modifier.CellCandidates.empty",
            return_value=empty_candidates,
        ) as empty:
            # ACT
            modifier.reset()

            # ASSERT
            assert state.cell_candidates == [empty_candidates] * 81
            assert empty.call_count == 81

    def test_reset_sets_all_value_candidates_to_empty(self, modifier, state):
        # ARRANGE
        empty_candidates = MagicMock(CellCandidates)

        with patch(
            "sudoku_strategy.grid.modifier.Cells",
            return_value=empty_candidates,
        ) as empty:
            # ACT
            modifier.reset()

            # ASSERT
            assert state.value_candidates == [empty_candidates] * 10
            assert empty.call_count == 10

    def test_reset_updates_filled_cells(self, modifier, state):
        # ACT
        modifier.reset()

        # ASSERT
        state.fill_filled_cells.assert_called_once()

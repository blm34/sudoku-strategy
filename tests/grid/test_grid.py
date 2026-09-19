from unittest.mock import Mock, patch

import pytest

from sudoku_strategy.grid import GridAnalysis, GridModifier, GridState
from sudoku_strategy.grid.grid import Grid


class TestGrid:
    @pytest.fixture
    def state(self):
        return Mock(GridState)

    @pytest.fixture
    def modifier(self, state):
        return Mock(GridModifier, _state=state)

    @pytest.fixture
    def analysis(self, state):
        return Mock(GridAnalysis, _state=state)

    def test_grid_initialises_with_attributes(self, state, modifier, analysis):
        # ACT
        grid = Grid(state, modifier, analysis)

        # ASSERT
        assert grid._state is state
        assert grid.modify is modifier
        assert grid.analyse is analysis

    def test_grid_initialiser_fails_if_analysis_has_different_state(
        self,
        state,
        modifier,
        analysis,
    ):
        # ARRANGE
        analysis_state = Mock(GridState)
        analysis._state = analysis_state

        # ACT
        with pytest.raises(
            ValueError,
            match="Grid analysis doesn't reference the same state object as the Grid object.",
        ):
            Grid(state, modifier, analysis)

    def test_grid_initialiser_fails_if_modifier_has_different_state(
        self,
        state,
        modifier,
        analysis,
    ):
        # ARRANGE
        modifier_state = Mock()
        modifier._state = modifier_state

        # ACT
        with pytest.raises(
            ValueError,
            match="Grid modifier doesn't reference the same state object as the Grid object.",
        ):
            Grid(state, modifier, analysis)

    def test_from_state_creates_grid_components(self, state, modifier, analysis):
        # ARRANGE
        cell_groups = Mock()

        with (
            patch(
                "sudoku_strategy.grid.grid.CellGroups",
                return_value=cell_groups,
            ) as cell_groups_cls,
            patch(
                "sudoku_strategy.grid.grid.GridModifier",
                return_value=modifier,
            ) as modifier_cls,
            patch(
                "sudoku_strategy.grid.grid.GridAnalysis",
                return_value=analysis,
            ) as analysis_cls,
        ):
            # ACT
            grid = Grid.from_state(state)

        # ASSERT
        cell_groups_cls.assert_called_once_with(state)
        modifier_cls.assert_called_once_with(state, cell_groups)
        analysis_cls.assert_called_once_with(state, cell_groups)

        assert grid._state is state
        assert grid.modify is modifier
        assert grid.analyse is analysis

    def test_new_puzzle_creates_state_from_puzzle_digits(self):
        # ARRANGE
        puzzle_digits = (5, 3, 0, 0, 7, 0, 0, 0, 0)

        with patch(
            "sudoku_strategy.grid.grid.GridState.new_puzzle",
        ) as new_puzzle:
            # ACT
            Grid.new_puzzle(puzzle_digits)

        # ASSERT
        new_puzzle.assert_called_once_with(puzzle_digits)

    def test_new_puzzle_creates_grid_from_state(self, state):
        # ARRANGE
        puzzle_digits = (5, 3, 0, 0, 7, 0, 0, 0, 0)
        resulting_grid = Mock()

        with (
            patch("sudoku_strategy.grid.grid.GridState.new_puzzle", return_value=state),
            patch(
                "sudoku_strategy.grid.grid.Grid.from_state", return_value=resulting_grid
            ) as grid_from_state,
        ):
            result = Grid.new_puzzle(puzzle_digits)

        # ASSERT
        grid_from_state.assert_called_once_with(state)
        assert result is resulting_grid

    def test_copy_makes_a_copy_of_the_state(self, state, analysis, modifier):
        # ARRANGE
        grid = Grid(state, modifier, analysis)

        # ACT
        grid.copy()

        # ASSERT
        state.copy.assert_called_once()

    def test_copy_returns_a_new_grid_from_the_copied_state(
        self,
        state,
        analysis,
        modifier,
    ):
        # ARRANGE
        copied_state = Mock()
        state.copy.return_value = copied_state

        grid = Grid(state, modifier, analysis)
        copied_grid = Mock()

        with patch(
            "sudoku_strategy.grid.grid.Grid.from_state",
            return_value=copied_grid,
        ) as from_state:
            # ACT
            copy = grid.copy()

        # ASSERT
        from_state.assert_called_once_with(copied_state)
        assert copy is copied_grid

from unittest.mock import Mock, call

import pytest

from sudoku_strategy.grid import (
    Cell,
    CellGroups,
    Grid,
    GridAnalysis,
    GridModifier,
    GridState,
)
from sudoku_strategy.solver.solver import Solver
from sudoku_strategy.strategy import Deduction
from sudoku_strategy.strategy.abs_strategy import AbsStrategy
from sudoku_strategy.strategy.deduction import CellDigit


class TestSolver:
    @pytest.fixture
    def state(self):
        return GridState.create_empty()

    @pytest.fixture
    def cell_groups(self, state):
        return CellGroups(state)

    @pytest.fixture
    def analysis(self, state, cell_groups):
        return GridAnalysis(state, cell_groups)

    @pytest.fixture
    def modifier(self, state, cell_groups):
        return GridModifier(state, cell_groups)

    @pytest.fixture
    def grid(self, analysis, modifier, state):
        return Grid(state, modifier, analysis)

    def test_find_next_returns_deduction_from_first_strategy(self, grid, analysis):
        # ARRANGE
        first_strategy = Mock(AbsStrategy)
        second_strategy = Mock(AbsStrategy)

        deduction = Mock(Deduction)

        first_strategy.find.return_value = deduction

        solver = Solver(strategies=(first_strategy, second_strategy))

        # ACT
        result = solver.find_next(grid)

        # ASSERT
        assert result is deduction
        first_strategy.find.assert_called_once_with(analysis)
        second_strategy.find.assert_not_called()

    def test_find_next_tries_next_strategy_when_first_finds_nothing(
        self, grid, analysis
    ):
        # ARRANGE
        first_strategy = Mock(AbsStrategy)
        second_strategy = Mock(AbsStrategy)

        deduction = Mock(Deduction)

        first_strategy.find.return_value = None
        second_strategy.find.return_value = deduction

        solver = Solver(strategies=(first_strategy, second_strategy))

        # ACT
        result = solver.find_next(grid)

        # ASSERT
        assert result is deduction

        first_strategy.find.assert_called_once_with(analysis)
        second_strategy.find.assert_called_once_with(analysis)

    def test_find_next_returns_none_when_no_strategy_finds_deduction(
        self, grid, analysis
    ):
        # ARRANGE
        first_strategy = Mock(AbsStrategy)
        second_strategy = Mock(AbsStrategy)

        first_strategy.find.return_value = None
        second_strategy.find.return_value = None

        solver = Solver(strategies=(first_strategy, second_strategy))

        # ACT
        result = solver.find_next(grid)

        # ASSERT
        assert result is None

        first_strategy.find.assert_called_once_with(analysis)
        second_strategy.find.assert_called_once_with(analysis)

    def test_solve_uses_copy_of_grid(self, grid):
        # ARRANGE
        working_grid = Mock(Grid)
        working_analysis = Mock(GridAnalysis)
        working_grid.analyse = working_analysis

        grid.copy = Mock(return_value=working_grid)
        working_analysis.is_complete.side_effect = [True]

        solver = Solver()

        # ACT
        result = solver.solve(grid)

        # ASSERT
        grid.copy.assert_called_once()
        working_analysis.is_complete.assert_called_once()
        assert result == []

    def test_solve_finds_and_applies_deductions(self, grid, modifier):
        # ARRANGE
        grid.copy = Mock(return_value=grid)
        grid.analyse.is_complete = Mock(side_effect=[False, True])
        grid.modify.apply = Mock()

        assignment = CellDigit(Cell(5), 7)
        deduction = Deduction(strategy="", explanation="", assignment=assignment)

        solver = Solver()
        solver.find_next = Mock(side_effect=[deduction])

        # ACT
        result = solver.solve(grid)

        # ASSERT
        assert result == [deduction]

        grid.copy.assert_called_once()
        modifier.apply.assert_called_once_with(deduction)

    def test_solve_finds_and_applies_multiple_deductions(self, grid, modifier):
        # ARRANGE
        grid.copy = Mock(return_value=grid)
        grid.analyse.is_complete = Mock(side_effect=[False, False, True])
        grid.modify.apply = Mock()

        first_assignment = CellDigit(Cell(5), 7)
        first_deduction = Deduction(
            strategy="", explanation="first", assignment=first_assignment
        )
        second_assignment = CellDigit(Cell(9), 2)
        second_deduction = Deduction(
            strategy="", explanation="second", assignment=second_assignment
        )

        solver = Solver()
        solver.find_next = Mock(side_effect=[first_deduction, second_deduction])

        # ACT
        result = solver.solve(grid)

        # ASSERT
        assert result == [
            first_deduction,
            second_deduction,
        ]

        assert modifier.apply.call_args_list == [
            call(first_deduction),
            call(second_deduction),
        ]

    def test_solve_stops_when_no_deduction_is_found(self, grid):
        # ARRANGE
        grid.copy = Mock(return_value=grid)
        grid.analyse.is_complete = Mock(return_value=False)

        solver = Solver()
        solver.find_next = Mock(return_value=None)

        # ACT
        result = solver.solve(grid)

        # ASSERT
        assert result == []

    def test_solve_logs_warning_when_no_deduction_is_found(self, grid, caplog):
        # ARRANGE
        grid.copy = Mock(return_value=grid)
        grid.analyse.is_complete = Mock(return_value=False)

        solver = Solver()
        solver.find_next = Mock(return_value=None)

        # ACT
        solver.solve(grid)

        # ASSERT
        assert "No next step found for puzzle." in caplog.text

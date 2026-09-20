from unittest.mock import MagicMock, Mock

import pytest

from sudoku_strategy.grid import Cell, Cells
from sudoku_strategy.strategy.deduction import CellDigit
from sudoku_strategy.strategy.pointing_pair import PointingPair, PointingPairStrategy


class TestPointingPairStrategy:
    @pytest.fixture
    def strategy(self):
        return PointingPairStrategy()

    def test_finds_pointing_pair_in_row(self, analysis, strategy):
        # ARRANGE
        first = Mock(Cell, row=0, col=0, box=0)
        second = Mock(Cell, row=0, col=1, box=0)
        third = Mock(Cell, row=0, col=2, box=0)
        fourth = MagicMock(Cell, row=0, col=3, box=1)
        fourth.configure_mock(**{"__str__.return_value": "R1C4"})

        box_cells = MagicMock(Cells)
        box_cells.__iter__.return_value = iter((first, second, third))
        box_cells.__len__.return_value = 3
        box_cells.first.return_value = first

        row_cells = MagicMock(Cells)
        row_cells.__iter__.return_value = iter((first, second, third, fourth))
        row_cells.__len__.return_value = 4
        row_cells.first.return_value = first

        analysis.cell_groups.box.return_value = box_cells
        analysis.get_cells_with_candidate.return_value = box_cells
        analysis.cell_groups.row.return_value = row_cells

        analysis.cell_has_candidate.return_value = True

        # ACT
        deduction = strategy.find(analysis)

        # ASSERT
        assert deduction is not None
        assert deduction.strategy == "Pointing Pair"
        assert deduction.eliminations == [CellDigit(fourth, 1)]
        assert deduction.explanation == (
            "Candidates for 1 in box 0 allow for eliminations in R1C4."
        )

    def test_finds_pointing_pair_in_column(self, analysis, strategy):
        # ARRANGE
        first = Mock(Cell, row=0, col=0, box=0)
        second = Mock(Cell, row=1, col=0, box=0)
        third = MagicMock(Cell, row=3, col=0, box=4)
        third.configure_mock(**{"__str__.return_value": "R4C1"})

        box_cells = (first, second, Mock(Cell, row=1, col=1, box=0))
        col_cells = (first, second, third)

        candidate_cells = MagicMock(Cells)
        candidate_cells.__len__.return_value = 2
        candidate_cells.__iter__.return_value = iter((first, second))
        candidate_cells.first.return_value = first

        analysis.cell_groups.box.return_value = box_cells
        analysis.get_cells_with_candidate.return_value = candidate_cells
        analysis.cell_groups.col.return_value = col_cells

        analysis.cell_has_candidate.return_value = True

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
        strategy._find_pointing_pairs = Mock(return_value=[])

        # ACT
        result = strategy.find(analysis)

        # ASSERT
        assert result is None

    def test_returns_none_when_pointing_pair_has_no_eliminations(
        self, analysis, strategy
    ):
        # ARRANGE
        first = Mock(Cell, row=0, col=0, box=0)
        second = Mock(Cell, row=0, col=1, box=0)
        third = Mock(Cell, row=0, col=2, box=0)
        fourth = Mock(Cell, row=0, col=3, box=1)

        box_cells = MagicMock(Cells)
        box_cells.__iter__.return_value = iter((first, second, third))

        row_cells = MagicMock(Cells)
        row_cells.__iter__.return_value = iter((first, second, third, fourth))

        analysis.cell_groups.box.return_value = box_cells
        analysis.get_cells_with_candidate.return_value = box_cells
        analysis.cell_has_candidate.return_value = False
        analysis.cell_groups.row.return_value = row_cells

        # ACT
        result = strategy.find(analysis)

        # ASSERT
        assert result is None

    def test_skips_candidate_when_more_than_three_cells_have_it(
        self, analysis, strategy
    ):
        # ARRANGE
        cells = (
            Mock(Cell, row=0, col=0),
            Mock(Cell, row=0, col=1),
            Mock(Cell, row=0, col=2),
            Mock(Cell, row=1, col=0),
        )

        analysis.cell_groups.box.return_value = cells
        analysis.get_cells_with_candidate.return_value = cells

        # ACT
        result = strategy.find(analysis)

        # ASSERT
        assert result is None

    def test_skips_digit_when_no_cells_have_candidate(self, analysis, strategy):
        # ARRANGE
        box_cells = (
            Mock(Cell, row=0, col=0),
            Mock(Cell, row=0, col=1),
        )

        analysis.cell_groups.box.return_value = box_cells
        analysis.get_cells_with_candidate.return_value = ()

        # ACT
        result = strategy.find(analysis)

        # ASSERT
        assert result is None

    def test_find_pointing_pairs_finds_first_pointing_pair_with_elimination(
        self, analysis, strategy
    ):
        # ARRANGE
        first = Mock(Cell, row=0, col=0, box=0)
        second = Mock(Cell, row=0, col=1, box=0)

        box_cells = MagicMock(Cells)
        box_cells.__iter__.return_value = iter((first, second))
        box_cells.first.return_value = first
        box_cells.__len__.return_value = 2

        row_cells = MagicMock(Cells)

        analysis.cell_groups.box.return_value = box_cells
        analysis.cell_groups.row.return_value = row_cells

        analysis.get_cells_with_candidate.side_effect = [(), box_cells]

        analysis.cell_has_candidate.side_effect = [True, False]

        # ACT
        pointing_pairs = strategy._find_pointing_pairs(analysis)

        # ASSERT
        result = next(pointing_pairs)
        assert result.digit == 2
        assert result.box == 0
        assert result.cells == row_cells

    def test_get_eliminations_ignores_cells_in_pointing_pair_box(
        self, analysis, strategy
    ):
        # ARRANGE
        box_cell = Mock(Cell, row=0, col=0, box=0)
        elimination_cell = Mock(Cell, row=0, col=3, box=1)

        cells = MagicMock(Cells)
        cells.__iter__.return_value = iter((box_cell, elimination_cell))

        pointing_pair = PointingPair(
            digit=5,
            box=0,
            cells=cells,
        )

        analysis.cell_has_candidate.return_value = True

        # ACT
        eliminations = strategy._get_eliminations(
            analysis,
            pointing_pair,
        )

        # ASSERT
        assert eliminations == [CellDigit(elimination_cell, 5)]
        analysis.cell_has_candidate.assert_called_once_with(
            elimination_cell,
            5,
        )

    def test_get_eliminations_only_returns_cells_with_candidate(
        self,
        analysis,
        strategy,
    ):
        # ARRANGE
        first = Mock(Cell, row=0, col=0, box=1)
        second = Mock(Cell, row=0, col=1, box=2)
        third = Mock(Cell, row=0, col=2, box=3)

        cells = MagicMock(Cells)
        cells.__iter__.return_value = iter((first, second, third))

        pointing_pair = PointingPair(
            digit=7,
            box=0,
            cells=cells,
        )

        analysis.cell_has_candidate.side_effect = [True, False, True]

        # ACT
        eliminations = strategy._get_eliminations(
            analysis,
            pointing_pair,
        )

        # ASSERT
        assert eliminations == [
            CellDigit(first, 7),
            CellDigit(third, 7),
        ]

    def test_get_eliminations_returns_empty_when_no_cells_have_candidate(
        self, analysis, strategy
    ):
        # ARRANGE
        pointing_pair = PointingPair(
            digit=3,
            box=0,
            cells=MagicMock(Cells),
        )

        analysis.cell_has_candidate.return_value = False

        # ACT
        eliminations = strategy._get_eliminations(
            analysis,
            pointing_pair,
        )

        # ASSERT
        assert eliminations == []

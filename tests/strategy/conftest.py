from unittest.mock import Mock

import pytest

from sudoku_strategy.grid import CellGroups, GridAnalysis, GridState


@pytest.fixture
def analysis():
    analysis = Mock(GridAnalysis)

    analysis._state = Mock(GridState)
    analysis.cell_groups = Mock(CellGroups)

    return analysis

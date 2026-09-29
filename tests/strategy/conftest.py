import pytest

from sudoku_strategy.grid import CellGroups, GridAnalysis, GridState


@pytest.fixture
def state() -> GridState:
    return GridState.create_empty()


@pytest.fixture
def cell_groups(state) -> CellGroups:
    return CellGroups(state)


@pytest.fixture
def analysis(state, cell_groups) -> GridAnalysis:
    return GridAnalysis(state, cell_groups)

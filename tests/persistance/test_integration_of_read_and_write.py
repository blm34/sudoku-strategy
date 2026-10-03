from io import StringIO

from hypothesis import given
from hypothesis import strategies as st

from sudoku_strategy.grid import CellCandidates, Grid, GridState
from sudoku_strategy.persistance.readers import JsonReader, SusserReader
from sudoku_strategy.persistance.writers import JsonWriter, SusserWriter

st_sudoku_digit = st.integers(min_value=0, max_value=9)
st_sudoku_digits = st.lists(st_sudoku_digit, min_size=81, max_size=81)

st_cell_candidate = st.builds(
    CellCandidates,
    st.integers(min_value=0, max_value=0b111111111),
)
st_cell_candidates = st.lists(st_cell_candidate, min_size=81, max_size=81)


@st.composite
def grid_states(draw):
    puzzle_digits = draw(st_sudoku_digits)

    digits = [
        draw(st_sudoku_digit if puzzle_digit == 0 else st.just(puzzle_digit))
        for puzzle_digit in puzzle_digits
    ]

    cell_candidates = draw(st_cell_candidates)

    state = GridState.new_puzzle(tuple(digits))
    state.digits = digits
    state.cell_candidates = cell_candidates

    return state


@given(state=grid_states())
def test_susser_round_trip(state):
    # ARRANGE
    original = Grid.from_state(state)

    stream = StringIO()

    # ACT
    SusserWriter().write(original, stream)

    stream.seek(0)

    result = SusserReader().read(stream)

    # ASSERT
    assert result._state.digits == original._state.digits


@given(state=grid_states())
def test_json_round_trip(state):
    # ARRANGE
    original = Grid.from_state(state)

    stream = StringIO()

    # ACT
    JsonWriter().write(original, stream)

    stream.seek(0)

    result = JsonReader().read(stream)

    # ASSERT
    assert result._state.digits == state.digits

    assert result._state.puzzle_digits == state.puzzle_digits

    for idx in range(81):
        assert (
            result._state.cell_candidates[idx]._mask == state.cell_candidates[idx]._mask
        )

from io import StringIO

from sudoku_strategy.grid import CellCandidates, Grid, GridState
from sudoku_strategy.persistance.readers import JsonReader, SusserReader
from sudoku_strategy.persistance.writers import JsonWriter, SusserWriter


def test_susser_round_trip():
    # ARRANGE
    original_state = GridState.create_empty()
    original_state.digits = list(range(1, 10)) * 9
    original = Grid.from_state(original_state)

    stream = StringIO()

    # ACT
    SusserWriter().write(original, stream)

    stream.seek(0)

    result = SusserReader().read(stream)

    # ASSERT
    assert result._state.digits == original._state.digits


def test_json_round_trip():
    # ARRANGE
    puzzle_digits = [0] * 81
    for val, idx in enumerate(range(0, 81, 10), start=1):
        puzzle_digits[idx] = val

    original_state = GridState.new_puzzle(tuple(puzzle_digits))

    original_state.digits[1] = 4
    original_state.digits[2] = 5
    original_state.digits[9] = 6

    original_state.cell_candidates[3] = CellCandidates(0b111100110)
    original_state.cell_candidates[4] = CellCandidates(0b111100110)
    original_state.cell_candidates[5] = CellCandidates(0b111100110)

    original = Grid.from_state(original_state)

    stream = StringIO()

    # ACT
    JsonWriter().write(original, stream)

    stream.seek(0)

    result = JsonReader().read(stream)

    # ASSERT
    assert result._state.digits == original._state.digits

import json
from io import StringIO

import pytest

from sudoku_strategy.persistance.readers.json import JsonReader


class TestJsonReader:
    @pytest.fixture
    def reader(self):
        return JsonReader()

    def test_reads_puzzle_digits(self, reader):
        # ARRANGE
        puzzle_digits = [1, 2, 3] + [0] * 78
        text = json.dumps(
            {
                "puzzle_digits": puzzle_digits,
                "digits": [0] * 81,
                "candidate_values": [[] for _ in range(81)],
            }
        )
        stream = StringIO(text)

        # ACT
        grid = reader.read(stream)

        # ASSERT
        state = grid._state
        assert state.puzzle_digits[0] == 1
        assert state.puzzle_digits[1] == 2
        assert state.puzzle_digits[2] == 3
        assert all(digit == 0 for digit in state.puzzle_digits[3:])

    def test_leaves_empty_puzzle_cells_unset(self, reader):
        # ARRANGE
        text = json.dumps(
            {
                "puzzle_digits": [0] * 81,
                "digits": [0] * 81,
                "candidate_values": [[] for _ in range(81)],
            }
        )
        stream = StringIO(text)

        # ACT
        grid = reader.read(stream)

        # ASSERT
        assert all(digit == 0 for digit in grid._state.puzzle_digits)

    def test_reads_digits_into_correct_cells(self, reader):
        # ARRANGE
        digits = [0] * 81
        digits[0] = 1
        digits[40] = 5
        digits[80] = 9

        text = json.dumps(
            {
                "puzzle_digits": [0] * 81,
                "digits": digits,
                "candidate_values": [[] for _ in range(81)],
            }
        )
        stream = StringIO(text)

        # ACT
        grid = reader.read(stream)

        # ASSERT
        state = grid._state
        assert state.digits[0] == 1
        assert state.digits[40] == 5
        assert state.digits[80] == 9

    def test_reads_candidate_values_into_correct_cells(self, reader):
        # ARRANGE
        candidate_values = [[] for _ in range(81)]
        candidate_values[0] = [1, 2, 3]
        candidate_values[40] = [4, 5, 6]
        candidate_values[80] = [7, 8, 9]

        text = json.dumps(
            {
                "puzzle_digits": [0] * 81,
                "digits": [0] * 81,
                "candidate_values": candidate_values,
            }
        )
        stream = StringIO(text)

        # ACT
        grid = reader.read(stream)

        # ASSERT
        state = grid._state
        assert state.cell_candidates[0]._mask == 0b000000111
        assert state.cell_candidates[40]._mask == 0b000111000
        assert state.cell_candidates[80]._mask == 0b111000000

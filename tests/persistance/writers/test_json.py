import json
from io import StringIO

import pytest

from sudoku_strategy.grid import Cell, CellCandidates, Grid, GridState
from sudoku_strategy.persistance.writers.json import JsonWriter


class TestJsonWriter:
    @pytest.fixture
    def writer(self):
        return JsonWriter()

    def test_writes_puzzle_digits(self, writer):
        # ARRANGE
        puzzle_digits = [1, 2, 3] + [0] * 78
        state = GridState.new_puzzle(tuple(puzzle_digits))
        grid = Grid.from_state(state)

        stream = StringIO()

        # ACT
        writer.write(grid, stream)

        # ASSERT
        grid_dict = json.loads(stream.getvalue())

        assert grid_dict["puzzle_digits"] == puzzle_digits

    def test_writes_digits_into_correct_cells(self, writer):
        # ARRANGE
        state = GridState.create_empty()
        grid = Grid.from_state(state)

        grid.modify.write_digit(1, Cell(0))
        grid.modify.write_digit(5, Cell(40))
        grid.modify.write_digit(9, Cell(80))

        stream = StringIO()

        # ACT
        writer.write(grid, stream)

        # ASSERT
        grid_dict = json.loads(stream.getvalue())

        assert grid_dict["digits"][0] == 1
        assert grid_dict["digits"][40] == 5
        assert grid_dict["digits"][80] == 9

    def test_writes_empty_digits_as_zero(self, writer):
        # ARRANGE
        state = GridState.create_empty()
        grid = Grid.from_state(state)
        stream = StringIO()

        # ACT
        writer.write(grid, stream)

        # ASSERT
        grid_dict = json.loads(stream.getvalue())

        assert all(digit == 0 for digit in grid_dict["digits"])

    def test_writes_candidate_digits_into_correct_cells(self, writer):
        # ARRANGE
        state = GridState.create_empty()
        state.cell_candidates[0] = CellCandidates(0b000000111)
        state.cell_candidates[40] = CellCandidates(0b000111000)
        state.cell_candidates[80] = CellCandidates(0b111000000)

        grid = Grid.from_state(state)

        stream = StringIO()

        # ACT
        writer.write(grid, stream)

        # ASSERT
        grid_dict = json.loads(stream.getvalue())

        assert grid_dict["candidate_values"][0] == [1, 2, 3]
        assert grid_dict["candidate_values"][40] == [4, 5, 6]
        assert grid_dict["candidate_values"][80] == [7, 8, 9]

    def test_writes_empty_candidate_values_as_empty_lists(self, writer):
        # ARRANGE
        state = GridState.create_empty()
        grid = Grid.from_state(state)

        stream = StringIO()

        # ACT
        writer.write(grid, stream)

        # ASSERT
        grid_dict = json.loads(stream.getvalue())

        assert all(
            candidate_list == [] for candidate_list in grid_dict["candidate_values"]
        )

    def test_writes_all_grid_data(self, writer):
        # ARRANGE
        puzzle_digits = [0] * 81
        puzzle_digits[0] = 1
        puzzle_digits[40] = 5

        state = GridState.new_puzzle(tuple(puzzle_digits))
        grid = Grid.from_state(state)

        grid.modify.write_digit(2, Cell(1))
        grid.modify.write_digit(9, Cell(80))

        grid.modify.add_candidates([3, 4, 5], Cell(10))
        grid.modify.add_candidates([6, 7, 8], Cell(63))

        stream = StringIO()

        # ACT
        writer.write(grid, stream)

        # ASSERT
        grid_dict = json.loads(stream.getvalue())

        assert grid_dict["puzzle_digits"] == puzzle_digits

        assert grid_dict["digits"][0] == 1
        assert grid_dict["digits"][1] == 2
        assert grid_dict["digits"][40] == 5
        assert grid_dict["digits"][80] == 9

        assert grid_dict["candidate_values"][10] == [3, 4, 5]
        assert grid_dict["candidate_values"][63] == [6, 7, 8]

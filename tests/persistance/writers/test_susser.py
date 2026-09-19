from io import StringIO

import pytest

from sudoku_strategy.grid import Grid, GridState
from sudoku_strategy.persistance.writers.susser import SusserWriter


class TestSusserWriter:
    @pytest.fixture
    def writer(self):
        return SusserWriter()

    def test_writes_empty_cells_as_dots(self, writer):
        # ARRANGE
        state = GridState.create_empty()
        grid = Grid.from_state(state)

        stream = StringIO()

        # ACT
        writer.write(grid, stream)

        # ASSERT
        assert stream.getvalue() == "." * 81

    def test_writes_zero_and_digits_correctly(self, writer):
        # ARRANGE
        digits = [0] * 81
        digits[0] = 5
        digits[40] = 7
        digits[80] = 3

        state = GridState.new_puzzle(tuple(digits))
        grid = Grid.from_state(state)

        stream = StringIO()

        # ACT
        writer.write(grid, stream)

        # ASSERT
        output = stream.getvalue()

        assert len(output) == 81
        assert output[0] == "5"
        assert output[40] == "7"
        assert output[80] == "3"

    def test_writes_digits_in_grid_order(self, writer):
        # ARRANGE
        digits = tuple(range(1, 10)) * 9

        state = GridState.new_puzzle(digits)
        grid = Grid.from_state(state)

        stream = StringIO()

        # ACT
        writer.write(grid, stream)

        # ASSERT
        assert stream.getvalue() == "".join(str(digit) for digit in digits)

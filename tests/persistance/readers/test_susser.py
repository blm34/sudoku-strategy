from io import StringIO

import pytest

from sudoku_strategy.persistance.readers.susser import SusserReader


class TestSusserReader:
    @pytest.fixture
    def reader(self):
        return SusserReader()

    def test_reads_complete_grid(self, reader):
        # ARRANGE
        text = (
            "123456789"
            "456789123"
            "789123456"
            "234567891"
            "567891234"
            "891234567"
            "345678912"
            "678912345"
            "912345678"
        )
        stream = StringIO(text)

        # ACT
        grid = reader.read(stream)

        # ASSERT
        assert all(
            grid._state.puzzle_digits[idx] == int(char) for idx, char in enumerate(text)
        )

    def test_reads_digits_into_correct_cells(self, reader):
        # ARRANGE
        text = "1" + "." * 80
        stream = StringIO(text)

        # ACT
        grid = reader.read(stream)

        # ASSERT
        state = grid._state
        assert state.puzzle_digits[0] == 1
        assert all(digit == 0 for digit in state.puzzle_digits[1:])

    def test_leaves_empty_cells_unset(self, reader):
        # ARRANGE
        text = "." * 81
        stream = StringIO(text)

        # ACT
        grid = reader.read(stream)

        # ASSERT
        assert all(val == 0 for val in grid._state.puzzle_digits)

    @pytest.mark.parametrize("empty", ["0", ".", "X", "*", "_"])
    def test_supports_preferred_empty_characters(self, reader, empty):
        # ARRANGE
        text = "5" + empty * 80
        stream = StringIO(text)

        # ACT
        grid = reader.read(stream)

        # ASSERT
        state = grid._state
        assert state.puzzle_digits[0] == 5
        assert all(digit == 0 for digit in state.puzzle_digits[1:])

    def test_raises_error_when_input_is_too_short(self, reader):
        # ARRANGE
        text = "." * 80
        stream = StringIO(text)

        # ACT / ASSERT
        with pytest.raises(ValueError, match="Expected 81 characters but got 80"):
            reader.read(stream)

    def test_raises_error_when_input_is_too_long(self, reader):
        # ARRANGE
        text = "." * 82
        stream = StringIO(text)

        # ACT / ASSERT
        with pytest.raises(ValueError, match="Expected 81 characters but got 82"):
            reader.read(stream)

    def test_raises_error_when_empty_character_cannot_be_determined(self, reader):
        # ARRANGE
        text = "1" * 80 + "A"
        stream = StringIO(text)

        # ACT / ASSERT
        with pytest.raises(
            ValueError,
            match="Could not determine the 'empty' character",
        ):
            reader.read(stream)

    @pytest.mark.xfail(
        strict=True,
        reason="This functionality has not yet been implemented",
    )
    def test_can_determine_a_non_standard_empty_character(self, reader):
        # ARRANGE
        text = "1" * 80 + "A"
        stream = StringIO(text)

        # ACT
        grid = reader.read(stream)

        # ASSERT
        state = grid._state
        assert state.puzzle_digits[0] == 1
        assert all(digit == 0 for digit in state.puzzle_digits[1:])

    def test_digits_are_written_to_correct_cells(self, reader):
        # ARRANGE
        text = (
            "1........"
            "........."
            "........."
            "........."
            "....5...."
            "........."
            "........."
            "........."
            "........9"
        )
        stream = StringIO(text)

        # ACT
        grid = reader.read(stream)

        # ASSERT
        state = grid._state
        assert state.puzzle_digits[0] == 1
        assert state.puzzle_digits[40] == 5
        assert state.puzzle_digits[80] == 9

    @pytest.mark.parametrize(
        ("text", "expected"),
        [
            ("1" + "0" * 80, "0"),
            ("1" + "." * 80, "."),
            ("1" + "X" * 80, "X"),
            ("1" + "*" * 80, "*"),
            ("1" + "_" * 80, "_"),
        ],
    )
    def test_get_empty_character(self, reader, text, expected):
        # ACT
        char = reader._get_empty_character(text)

        assert char == expected

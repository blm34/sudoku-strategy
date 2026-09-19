"""
If there are 81 groups of digits, the data is interpreted as a candidate grid.
All formatting is ignored.

If there are N digits and 81-N occurrences of another character, this character
will be interpreted as representing an empty cell. When multiple characters add
up to 81, the following preference list is used: '0', '.', 'X', '*', '_', ' '
"""

from typing import TYPE_CHECKING

from sudoku_strategy.grid import Grid

from .interface import AbsSudokuReader

if TYPE_CHECKING:
    from typing import TextIO


class SusserReader(AbsSudokuReader):
    def read(self, stream: TextIO) -> Grid:
        """Read a susser format from a text stream"""
        text = stream.readline()
        if len(text) != 81:
            raise ValueError(f"Expected 81 characters but got {len(text)}")

        empty = self._get_empty_character(text)

        digits = []
        for char in text:
            if char == empty:
                digits.append(0)
            else:
                digits.append(int(char))

        return Grid.new_puzzle(tuple(digits))

    # TODO: This should work for any character - not just the 'prefered' ones
    def _get_empty_character(self, text: str) -> str:
        """Determine the character used to represent no digit."""
        valid_numbers = ("1", "2", "3", "4", "5", "6", "7", "8", "9")
        digit_count = sum(1 for char in text if char in valid_numbers)

        candidates = ("0", ".", "X", "*", "_", " ")
        for candidate in candidates:
            if text.count(candidate) + digit_count == 81:
                return candidate

        raise ValueError(
            "Could not determine the 'empty' character for the given puzzle."
        )

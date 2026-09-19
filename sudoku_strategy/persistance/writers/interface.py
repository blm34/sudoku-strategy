from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import TextIO

    from sudoku_strategy.grid import Grid


class AbsSudokuWriter(ABC):
    @abstractmethod
    def write(self, grid: Grid, stream: TextIO):
        """Write a sudoku to a text stream."""
        raise NotImplementedError

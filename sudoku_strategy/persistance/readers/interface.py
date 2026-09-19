from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import TextIO

    from sudoku_strategy.grid import Grid


class AbsSudokuReader(ABC):
    @abstractmethod
    def read(self, stream: TextIO) -> Grid:
        """Read a sukoku from a text stream."""
        raise NotImplementedError

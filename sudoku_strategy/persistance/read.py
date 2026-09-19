from typing import TYPE_CHECKING

from .readers import JsonReader, SusserReader

if TYPE_CHECKING:
    from pathlib import Path

    from sudoku_strategy.grid import Grid

    from .readers.interface import AbsSudokuReader


READERS = {
    ".txt": SusserReader,
    ".json": JsonReader,
}


class SudokuFileReader:
    def load(self, path: Path) -> Grid:
        reader = self._reader_for(path)

        with path.open("r") as stream:
            return reader.read(stream)

    def _reader_for(self, path: Path) -> AbsSudokuReader:
        extension = path.suffix
        reader = READERS.get(extension)

        if reader is None:
            raise ValueError(f"No reader found for {extension} file types.")

        return reader()

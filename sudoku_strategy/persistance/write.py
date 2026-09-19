from typing import TYPE_CHECKING

from .writers import JsonWriter, SusserWriter

if TYPE_CHECKING:
    from pathlib import Path

    from sudoku_strategy.grid import Grid

    from .writers.interface import AbsSudokuWriter


WRITERS = {
    ".txt": SusserWriter,
    ".json": JsonWriter,
}


class SudokuFileWriter:
    def save(self, grid: Grid, path: Path):
        writer = self._writer_for(path)

        with path.open("w") as stream:
            writer.write(grid, stream)

    def _writer_for(self, path: Path) -> AbsSudokuWriter:

        extension = path.suffix
        writer = WRITERS.get(extension)

        if writer is None:
            raise ValueError(f"No writer found for files of type {extension}")

        return writer()

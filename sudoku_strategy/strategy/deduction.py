from abc import ABC
from dataclasses import dataclass, field

from sudoku_strategy.grid import Cell


@dataclass(frozen=True)
class CellDigit:
    """Represents a cell and a digit corresponding to that cell."""

    cell: Cell
    digit: int


@dataclass(frozen=True)
class Deduction(ABC):
    """Abstract class for the result of a strategy."""

    strategy: str
    explanation: str
    eliminations: list[CellDigit] = field(default_factory=list)
    assignment: CellDigit | None = None

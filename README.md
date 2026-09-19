# Sudoku Strategy

A Python library for representing, analysing, and solving Sudoku puzzles using
human style solving techniques.

The project is designed around a simple distinction between:

* Grid state: the current digits and candidates in a puzzle.
* Grid analysis: information that can be derived from the current state.
* Strategies: human solving techniques that analyse a grid and identify
  deductions.
* Deductions: explanations of the changes that can be made to the puzzle.
* Grid modification: applying deductions to progress the puzzle.

The aim is not simply to produce a completed Sudoku grid, but to provide useful,
explainable solving steps that can be presented as hints.

## Installation

Install from PyPI with:

```bash
pip install sudoku_strategy
```

## Quick Start

```Python
from sudoku_strategy import Grid, Solver
from sudoku_strategy.grid import Cell

# Puzzle digits is an 81 length tuple representing the starting state of the
# puzzle. `0` is used to represent an empty cell.
puzzle_digits = (0, 0, 5, 4, 0, ...)

grid = Grid.new_puzzle(puzzle_digits)

# Add any user entered digits to the puzzle
grid.modify.write_digit(5, Cell.from_position(7, 8))

# Compute all candidates
grid.modify.compute_candidates()

# Get the next move
solver = Solver()

deduction = solver.find_next(grid)

if deduction is not None:
    print(deduction.explanation)
```

A deduction's explanation might look like:

`Cell R4C7 is a naked single with value 5`

This makes the solver suitable for applications where the user wants to
understand why a move can be made rather than simply being given the answer.

## Representing a Sudoku

### Grid

A Sudoku consists of 81 cells arranged into:

* 9 rows
* 9 columns
* 9 boxes

Each cell can contain one digit, or a number of candidates.

#### Cell

A Cell is represented using an index from 0-80 starting in the top left cell,
then working along each row to cell 80 in the bottom right. Properties are
available to get the row, column and box of the cell. These are all zero
indexed.

```Python
from sudoku_strategy import Cell

cell = Cell(33)

idx = row.index  # index = 33
row = cell.row  # row = 3
col = cell.col  # col = 6
box = cell.box  # box = 5
```

This corresponds to `R4C7` when displayed using the conventional one-based
Sudoku notation.

Cells can also be created from their (row, column) position in the grid 

```Python
cell = Cell.from_position(3, 6)
```

#### Cell Candidates

Cell candidates represent digits that could be placed in a cell. They contain a
set of numbers from 1-9. They can be created to contain any permutation of
digits.

```Python
from sudoku_strategy.grid import CellCandidates

# Create a `CellCandidates` object that contains no candidates
no_candidates = CellCandidates.empty()

# Create a `CellCandidates` object that contains all 9 candidates
all_candidates = CellCandidates.with_all()

# Create a `CellCandidates` object containing the given candidates
candidates = CellCandidates.from_digits([5, 6, 7])
```

Cell candidate objects can be manipulated by adding or removing candidates.
Addition and subtraction of integers can add and remove candidates, and bitwise
operations between two candidates objects can give unions and intersections.

#### Cells

`Cells` is an object to represent a collection of Cells. It supports addition
and subtraction with `Cell` objects to add or remove cells, and bitwise
operations with other `Cells` objects to perform unions or intersections.
Iterating over a `Cells` object will yield each `Cell` contained within it.

#### Grid

A `Grid` object represents a sudoku puzzle. It contains the current state of the
puzzle, as well as logic for modifying it and analysing it.

The grid can be analysed for various properties:

```Python
# Get the digit in the given cell
digit = grid.analysis.get_digit_in_cell(cell)

# Count how many cells out of the given cells have the given digit as a candidate
candidates = grid.analysis.count_cells_with_candidate(cells, digit)

# Has the puzzle been solved?
grid.analysis.is_complete()
```

The grid can be modified to change the set digits, or the candidates:

```Python
# Write 8 to R9C4
grid.modifiy.write_digit(5, Cell(8, 3))

# Calculate all candidate for the puzzle
grid.modify.update_candidates()

# Remove the candidate 6 from R3C8
grid.modify.remove_candidate(6, Cell(2, 7))

# Reset the puzzle to its starting state
grid.modify.reset()
```

## Solving Strategies

A solving strategy analyses a grid and produces a deduction when it finds one.
Strategies implement the `AbsStrategy` interface:

```Python
class AbsStrategy(ABC):
    @abstractmethod
    def find(self, analysis) -> Deduction | None: ...
```

For example, the naked single strategy looks for an empty cell with exactly one
remaining candidate:

```Python
from sudoku_strategy.strategy import NakedSingleStrategy

strategy = NakedSingleStrategy()

deduction = strategy.find(analysis)
```

If a naked single is found, the strategy returns a `Deduction`. If no naked
single exists, it returns `None`.

## Deductions

A deduction represents a conclusion reached by a solving strategy. A deduction
can either show a cell that can have a digit entered, or provide a list of
candidates that can be eliminated. For example:

```Python
from sudoku_strategy.strategy import Deduction

Deduction(
    strategy="Naked Single",
    assignment=CellDigit(Cell(3, 6), 5),
    explanation="Cell R4C7 is a naked single with value 5.",
)
```

A deduction contains both the information required to make the change, and an
explanation suitable for displaying to  user.

## Finding a Hint

The `Solver` can search its configured strategies for the next available
deduction

```Python
from sudoku_strategy import Solver

solver = Solver()

deduction = solver.find_next(grid)

if deduction is None:
    print("No known next step")
else:
    print(deduction.explanation)
```

Strategies are evaluated in order. The first strategy to produce a deduction
determines the next step. This means the order of strategies can be used to
control the solving approach. For example:

```Python
strategies = (
    NakedSingleStrategy(),
    HiddenSingleStrategy(),
)
solver = Solver(
    strategies=strategies,
)
```

## Solving a Puzzle

The solver can also repeatedly find and apply deductions until the puzzle is
complete or no further supported deduction can be found:

```Python
deductions = solver.solve(grid)
```

The returned list contains the deductions that were made. This allows the
solution to be displayed as a sequence of human-readable steps rather than only
displaying the final grid.

For example:

```Python
for deduction in deductions:
    print(deduction.explanation)
```

The original grid is preserved while solving - the solver works on a copy of the
supplied grid.

## Reading and Writing Puzzles

Puzzles can be read and written in various formats using `GridFileWriter` and
`GridFileReader` which convert file to/from a `GridState`:

```Python
from sudoku_strategy import GridFileWriter, GridFileReader

# Load a file into a Grid
grid = GridFileReader().load(path)

# Manipulate the grid
...

# Write the updated grid back to a file
GridFileWriter().save(grid, path)
```

Supported formats:

* Susser: saved in .txt files
* Json: saved in .json files

### Susser Format

A string of 81 characters representing cells in the grid, starting in the top
left, and working along the rows to the bottom right. Filled cells are given the
number 1-9, and empty cells use a placeholder character, e.g. '.'

### Json Format

The json format consists of an object with three fields:

* Puzzle digits
    * A list of 81 digits representing the puzzle's starting state. 0 is used to
      represent an empty cell
* digits
    * A list of 81 digits representing digits added to the grid. These include
      the digits defined in puzzle digits. 0 is used to represent an empty cell
* Candidates Values
    * A list of 81 lists. Each sub list can contain the numbers 1-9 representing
      the candidates for the associated cell.

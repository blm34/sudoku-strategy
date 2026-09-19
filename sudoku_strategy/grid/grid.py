from typing import TYPE_CHECKING

from .analysis import GridAnalysis
from .cell_groups import CellGroups
from .modifier import GridModifier
from .state import GridState

if TYPE_CHECKING:
    from typing import Self


class Grid:
    """Class to hold all logic around a puzzle grid.

    Attributes:
        modify: logic to mutate the grid
        analyse: logic for inferring from the grid

    Methods:
        from_state
        new_puzzle
        copy
    """

    def __init__(
        self,
        state: GridState,
        modifier: GridModifier,
        analysis: GridAnalysis,
    ):
        """Initialise a Grid object.

        Args:
            state: The state of the grid
            modifier: Logic for modify the state
            analysis: Logic for analysing the state
        """
        if modifier._state is not state:
            raise ValueError(
                "Grid modifier doesn't reference the same state object as the Grid object."
            )
        if analysis._state is not state:
            raise ValueError(
                "Grid analysis doesn't reference the same state object as the Grid object."
            )

        self._state = state
        self.modify = modifier
        self.analyse = analysis

    @classmethod
    def from_state(cls, state: GridState) -> Self:
        """Create a Grid object from a GridState.

        Args:
            state: The GridState object to create a grid for

        Returs:
            A grid object for the given GridState
        """
        cell_groups = CellGroups(state)
        modifier = GridModifier(state, cell_groups)
        analysis = GridAnalysis(state, cell_groups)
        return cls(state, modifier, analysis)

    @classmethod
    def new_puzzle(cls, puzzle_digits: tuple[int, ...]) -> Self:
        """Create a new Grid object given some puzzle digits.

        Args:
            puzzle_digits: The puzzle digits to use to make a Grid

        Returs:
            A Grid object containing the state of a new puzzle with the given digits
        """
        state = GridState.new_puzzle(puzzle_digits)
        return cls.from_state(state)

    def copy(self) -> Self:
        """Duplicate the Grid.

        Returns:
            A copy of the Grid
        """
        state = self._state.copy()
        return type(self).from_state(state)

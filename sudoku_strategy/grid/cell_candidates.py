from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator
    from typing import Self


class CellCandidates:
    """Store the candidate values for a single cell.

    Use a 9-bit bit mask to represent the candidates for a cell. The least
    significant bit is set to one if one is a candidate. Each subsequent bit
    is set to one if the next corresponding digit is a candidate.

    Methods:
        from_digits
        with_all
        empty
        remove_all
    """

    # Bit mask of 1s in every position that could be set
    _MASK = (1 << 9) - 1

    # Bit mask for each digit
    _DIGIT_MASKS = (0,) + tuple(1 << (digit - 1) for digit in range(1, 10))

    def __init__(self, mask: int):
        """Create a CellCandidates object from the given bit mask.

        Args:
            mask: The bit mask to use."""
        self._mask = mask

    @classmethod
    def from_digits(cls, digits: Iterable[int]) -> Self:
        """Create a CellCandidates object with the given digits as candidates.

        Args:
            digits: The digits to include as candidates

        Returns:
            A CellCandidates object containing the given digits
        """
        mask = sum(cls._mask_for_digit(digit) for digit in digits)
        return cls(mask)

    @classmethod
    def with_all(cls) -> Self:
        """Create a CellCandidates object with all candidates present.

        Returns:
            A CellCandidates object containing all digits
        """
        return cls(0b111111111)

    @classmethod
    def empty(cls) -> Self:
        """Create a CellCandidates object with no candidates present.

        Returns:
            A CellCandidates object containing no digits
        """
        return cls(0b000000000)

    def remove_all(self):
        """Remove all candidates."""
        self._mask = 0

    @classmethod
    def _mask_for_digit(cls, digit: int) -> int:
        """Calculate the bit mask for the given digit as a candidate.

        Args:
            digit: The candidate value to get a bit mask for.

        Returns:
            The bit mask representing the given digit.
        """
        return cls._DIGIT_MASKS[digit]

    def __iadd__(self, candidate: int) -> Self:
        """Add a candidate value."""
        mask = self._mask_for_digit(candidate)
        self._mask |= mask
        return self

    def __add__(self, candidate: int) -> CellCandidates:
        """Make a new CellCandidates object with a candidate added."""
        digit_mask = self._mask_for_digit(candidate)
        mask = self._mask | digit_mask
        return CellCandidates(mask)

    def __isub__(self, candidate: int) -> Self:
        """Remove a candidate value."""
        mask = self._mask_for_digit(candidate)
        self._mask &= ~mask
        return self

    def __sub__(self, candidate: int) -> CellCandidates:
        """Make a new CellCandidates object with a candidate removed."""
        digit_mask = self._mask_for_digit(candidate)
        mask = self._mask & ~digit_mask
        return CellCandidates(mask)

    def __iand__(self, other: CellCandidates) -> Self:
        """Intersection of the candidate values."""
        self._mask &= other._mask
        return self

    def __and__(self, other: CellCandidates) -> CellCandidates:
        """Get the intersection with the other set of candidates."""
        mask = self._mask & other._mask
        return CellCandidates(mask)

    def __ior__(self, other: CellCandidates) -> Self:
        """Union of the candidate values."""
        self._mask |= other._mask
        return self

    def __or__(self, other: CellCandidates) -> CellCandidates:
        """Get the union with the other set of candidates."""
        mask = self._mask | other._mask
        return CellCandidates(mask)

    def __invert__(self) -> CellCandidates:
        """Get the values that are not candidates."""
        mask = ~self._mask & self._MASK
        return CellCandidates(mask)

    def __eq__(self, other: object) -> bool:
        """Check equality of the candidates."""
        if not isinstance(other, CellCandidates):
            return NotImplemented

        return self._mask == other._mask

    def __contains__(self, digit: int) -> bool:
        """Is the given digit a candidate."""
        mask = self._mask_for_digit(digit)
        return bool(self._mask & mask)

    def __iter__(self) -> Iterator[int]:
        """Iterate over the candidates."""
        mask = self._mask

        while mask:
            bit = mask & -mask
            candidate = bit.bit_length()
            yield candidate
            mask ^= bit

    def __len__(self) -> int:
        """Number of candidates."""
        return self._mask.bit_count()

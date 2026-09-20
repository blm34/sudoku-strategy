import pytest

from sudoku_strategy.grid.cell_candidates import CellCandidates, NoCandidatesError


class TestCellCandidates:
    @pytest.mark.parametrize(
        ("digits", "expected_mask"),
        (
            ((1, 2, 3), 0b000000111),
            ((5, 7, 9), 0b101010000),
            ((1, 2, 3, 4, 5, 6, 7, 8, 9), 0b111111111),
            ((), 0b000000000),
            ((5,), 0b000010000),
            ((6, 8), 0b010100000),
        ),
    )
    def test_from_digits_gives_the_correct_mask(self, digits, expected_mask):
        # ACT
        candidates = CellCandidates.from_digits(digits)

        # ASSERT
        assert candidates._mask == expected_mask

    def test_with_all_gives_all_candidates(self):
        # ACT
        candidates = CellCandidates.with_all()

        # ASSERT
        assert candidates._mask == 0b111111111

    def test_empty_gives_no_candidates(self):
        # ACT
        candidates = CellCandidates.empty()

        # ASSERT
        assert candidates._mask == 0

    def test_remove_all_sets_bit_mask_to_0(self):
        # ARRANGE
        candidates = CellCandidates(0b110110100)

        # ACT
        candidates.remove_all()

        # ASSERT
        assert candidates._mask == 0b000000000

    @pytest.mark.parametrize(
        ("mask", "expected_digit"),
        (
            (0b000000001, 1),
            (0b111000100, 3),
            (0b100000000, 9),
            (0b000011000, 4),
        ),
    )
    def test_first_returns_smallest_candidate(self, mask, expected_digit):
        # ARRANGE
        candidates = CellCandidates(mask)

        # ACT
        digit = candidates.first()

        # ASSERT
        assert digit == expected_digit

    def test_first_raises_no_candidates_error_when_candidates_are_empty(self):
        # ARRANGE
        candidates = CellCandidates.empty()

        with pytest.raises(NoCandidatesError):
            # ACT
            candidates.first()

    @pytest.mark.parametrize(
        ("digit", "expected_mask"),
        (
            (1, 0b000000001),
            (2, 0b000000010),
            (3, 0b000000100),
            (4, 0b000001000),
            (5, 0b000010000),
            (6, 0b000100000),
            (7, 0b001000000),
            (8, 0b010000000),
            (9, 0b100000000),
        ),
    )
    def test_mask_for_digit_gives_correct_mask(self, digit, expected_mask):
        # ARRANGE
        candidates = CellCandidates.empty()

        # ACT
        mask = candidates._mask_for_digit(digit)

        # ASSERT
        assert mask == expected_mask

    def test_add_in_place_adds_candidate(self):
        # ARRANGE
        candidates = CellCandidates.empty()

        # ACT
        candidates += 4

        # ASSERT
        assert candidates._mask == 0b000001000

    def test_add_adds_candidate(self):
        # ARRANGE
        candidates = CellCandidates.empty()

        # ACT
        new_candidates = candidates + 4

        # ASSERT
        assert new_candidates._mask == 0b000001000

    def test_add_creates_new_candidate(self):
        # ARRANGE
        candidates = CellCandidates.empty()

        # ACT
        new_candidates = candidates + 5

        # ASSERT
        assert new_candidates is not candidates

    def test_subtract_in_place_subtracts_candidate(self):
        # ARRANGE
        candidates = CellCandidates(0b111111111)

        # ACT
        candidates -= 4

        # ASSERT
        assert candidates._mask == 0b111110111

    def test_subtract_subtracts_candidate(self):
        # ARRANGE
        candidates = CellCandidates(0b111111111)

        # ACT
        new_candidates = candidates - 7

        # ASSERT
        assert new_candidates._mask == 0b110111111

    def test_subtract_creates_new_candidate(self):
        # ARRANGE
        candidates = CellCandidates.empty()

        # ACT
        new_candidates = candidates - 5

        # ASSERT
        assert new_candidates is not candidates

    def test_and_in_place_gives_intersection_of_candidates(self):
        # ARRANGE
        candidates_1 = CellCandidates(0b001110000)
        candidates_2 = CellCandidates(0b100100010)

        # ACT
        candidates_1 &= candidates_2

        # ASSERT
        assert candidates_1._mask == 0b000100000

    def test_and_gives_intersection_of_candidates(self):
        # ARRANGE
        candidates_1 = CellCandidates(0b001110000)
        candidates_2 = CellCandidates(0b100100010)

        # ACT
        new_candidates = candidates_1 & candidates_2

        # ASSERT
        assert new_candidates._mask == 0b000100000

    def test_and_creates_new_candidates(self):
        # ARRANGE
        candidates_1 = CellCandidates(0b110001000)
        candidates_2 = CellCandidates(0b110011000)

        # ACT
        new_candidates = candidates_1 & candidates_2

        # ASSERT
        assert new_candidates is not candidates_1
        assert new_candidates is not candidates_2

    def test_or_in_place_gives_union_of_candidates(self):
        # ARRANGE
        candidates_1 = CellCandidates(0b001110000)
        candidates_2 = CellCandidates(0b100100010)

        # ACT
        candidates_1 |= candidates_2

        # ASSERT
        assert candidates_1._mask == 0b101110010

    def test_or_gives_union_of_candidates(self):
        # ARRANGE
        candidates_1 = CellCandidates(0b001110000)
        candidates_2 = CellCandidates(0b100100010)

        # ACT
        new_candidates = candidates_1 | candidates_2

        # ASSERT
        assert new_candidates._mask == 0b101110010

    def test_or_creates_new_candidates(self):
        # ARRANGE
        candidates_1 = CellCandidates(0b001110000)
        candidates_2 = CellCandidates(0b100100010)

        # ACT
        new_candidates = candidates_1 | candidates_2

        # ASSERT
        assert new_candidates is not candidates_1
        assert new_candidates is not candidates_2

    def test_invert_on_no_candidates_gives_all(self):
        # ARRANGE
        candidates = CellCandidates(0b000000000)

        # ACT
        inverted = ~candidates

        # ASSERT
        assert inverted._mask == 0b111111111

    def test_invert_on_all_candidates_gives_none(self):
        # ARRANGE
        candidates = CellCandidates(0b111111111)

        # ACT
        inverted = ~candidates

        # ASSERT
        assert inverted._mask == 0b000000000

    def test_invert_gives_complementary_candidates(self):
        # ARRANGE
        candidates = CellCandidates(0b101010101)

        # ACT
        inverted = ~candidates

        # ASSERT
        assert inverted._mask == 0b010101010

    def test_equality_for_same_candidates_is_true(self):
        # ARRANGE
        candidates_1 = CellCandidates(0b111100000)
        candidates_2 = CellCandidates(0b111100000)

        # ACT
        equal = candidates_1 == candidates_2

        # ASSERT
        assert equal

    def test_equality_for_different_candidates_is_false(self):
        # ARRANGE
        candidates_1 = CellCandidates(0b111101000)
        candidates_2 = CellCandidates(0b111100000)

        # ACT
        equal = candidates_1 == candidates_2

        # ASSERT
        assert not equal

    def test_equality_for_non_cell_candidates_type_returns_false(self):
        # ARRANGE
        candidates = CellCandidates(0b111101000)

        # ACT
        equal = candidates == 5

        # ASSERT
        assert not equal

    @pytest.mark.parametrize(
        "mask, candidate",
        (
            (0b111011111, 6),
            (0b000011001, 7),
            (0b001110000, 1),
            (0b011011010, 9),
        ),
    )
    def test_contains_returns_false_for_candidates_that_do_not_exist(
        self, mask, candidate
    ):
        # ARRANGE
        candidates = CellCandidates(mask)

        # ACT
        contained = candidate in candidates

        # ASSERT
        assert not contained

    @pytest.mark.parametrize(
        "mask, candidate",
        (
            (0b000100000, 6),
            (0b001000100, 7),
            (0b000000001, 1),
            (0b100000000, 9),
        ),
    )
    def test_contains_returns_true_for_candidates_that_exist(self, mask, candidate):
        # ARRANGE
        candidates = CellCandidates(mask)

        # ACT
        contained = candidate in candidates

        # ASSERT
        assert contained

    def test_iter_gives_correct_candidates(self):
        # ARRANGE
        candidates = CellCandidates(0b001101101)

        # ACT
        list_candidates = list(candidates)

        # ASSERT
        assert list_candidates == [1, 3, 4, 6, 7]

    @pytest.mark.parametrize(
        "mask, expected",
        (
            (0b000000000, 0),
            (0b111111111, 9),
            (0b110110000, 4),
            (0b000001001, 2),
            (0b110010011, 5),
        ),
    )
    def test_len_gives_count_of_candidates(self, mask, expected):
        # ARRANGE
        candidates = CellCandidates(mask)

        # ACT
        count = len(candidates)

        # ASSERT
        assert count == expected

from yahtzee_locals import *
from yahtzee_config import *
#miscellaneous stuff (mostly testcases) for temporary quick testing
categoryTests = [
    # Yahtzee
    ((5,0,0,0,0,0), "yahtzee", True),
    ((4,1,0,0,0,0), "yahtzee", False),

    # Three of a Kind
    ((0,3,0,1,1,0), "three_of_a_kind", True),
    ((0,2,0,2,1,0), "three_of_a_kind", False),

    # Four of a Kind
    ((1,0,4,0,0,0), "four_of_a_kind", True),
    ((2,0,3,0,0,0), "four_of_a_kind", False),

    # Full House
    ((0,3,0,0,2,0), "full_house", True),
    ((0,2,0,0,3,0), "full_house", True),
    ((1,4,0,0,0,0), "full_house", False),
    ((0,0,0,0,0,5), "full_house", False),

    # Small Straight
    ((1,1,1,1,0,1), "small_straight", True),
    ((1,2,1,1,0,0), "small_straight", True),
    ((0,1,1,1,2,0), "small_straight", True),
    ((0,0,2,1,1,1), "small_straight", True),
    ((1,1,1,0,1,1), "small_straight", False),

    # Large Straight
    ((1,1,1,1,1,0), "large_straight", True),
    ((0,1,1,1,1,1), "large_straight", True),
    ((1,2,0,1,1,0), "large_straight", False),

    # Chance
    ((2,1,1,1,0,0), "chance", True),
    ((0,0,0,0,0,5), "chance", True),

    ((1,1,1,1,1,0), "small_straight", True),
    ((0,1,1,1,1,1), "small_straight", True),
    ((2,1,1,1,0,0), "small_straight", True),
    ((0,2,1,1,1,0), "small_straight", True),
    ((0,0,0,0,0,5), "three_of_a_kind", True),
    ((0,0,0,0,0,5), "four_of_a_kind", True),
]

rerollGeneratorTests = [
    ((5,0,0,0,0,0), 6),
    ((1,1,1,1,1,0), 32),
    ((2,1,1,1,0,0), 24),
    ((0,3,0,2,0,0), 12),
]

gameTests = [
    ([
        ((5,0,0,0,0,0), ONES, 5),
        ((0,5,0,0,0,0), TWOS, 10),
        ((0,0,5,0,0,0), THREES, 15),
        ((0,0,0,5,0,0), FOURS, 20),
        ((0,0,0,0,5,0), FIVES, 60), #upper section bonus
        ((0,0,0,0,0,5), SIXES, 30),
    ], 0b0000000111111, 63),
    ([
        ((3,2,0,0,0,0), FULL_HOUSE, constScore if (constScore:=constScoreCategories[FULL_HOUSE]) else 7),
        ((1,1,1,1,1,0), LARGE_STRAIGHT, constScoreCategories[LARGE_STRAIGHT]),
        ((0,0,0,0,0,5), YAHTZEE, 50),
        ((4,0,1,0,0,0), FOUR_OF_A_KIND, 7),
        ((2,2,0,0,1,0), THREE_OF_A_KIND, 0),
    ], 0b1011110000000, 0)
]
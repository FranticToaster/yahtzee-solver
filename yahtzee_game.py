import logging
from yahtzee_locals import *
from yahtzee_config import *
from yahtzee_init import *
from typing import TypeAlias, cast

logger = logging.getLogger(__name__)

# use legacy TypeAlias for pre-3.12 pypy
Game: TypeAlias = tuple[int, int, int, Dices, int, bool]
GameWithDiceAsIndex: TypeAlias = tuple[
    int, int, int, int, int, bool
]  # dices represented as index
# access indexes
TURNS_LEFT_INDEX = 0
USED_CATEGORIES_INDEX = 1
UPPER_SECTION_SCORE_INDEX = 2
DICES_INDEX = 3
ROLLS_LEFT_INDEX = 4
YAHTZEE_DISABLED_INDEX = 5


def initGame() -> GameWithDiceAsIndex:
    return (
        4,  # turnsLeft
        0,  # usedCategories
        0,  # upperSectionScore
        999,  # dices; 999 should raise index out of bounds if access is attempted
        3,  # rollsLeft
        False,  # yahtzeeDisabled
    )


def initGameWithDicesAsTuple() -> Game:
    return (
        4,
        0,
        0,
        (0, 0, 0, 0, 0, 0),
        3,
        False,
    )


def moveFitsReq(
    category: Category,
    game: Game,
) -> bool:
    dices = game[DICES_INDEX]
    """Checks if a category claim fits the requirements of the category.
    Does not check if category has been used."""
    # big elif block below
    if category <= SIXES:
        return dices[category] > 0

    elif category == SMALL_STRAIGHT:
        return any(all(dices[j] > 0 for j in range(i, i + 4)) for i in range(3))

    elif category == LARGE_STRAIGHT:
        return dices == (1, 1, 1, 1, 1, 0) or dices == (0, 1, 1, 1, 1, 1)

    elif category == THREE_OF_A_KIND:
        return any(dices[i] >= 3 for i in range(6))

    elif category == FOUR_OF_A_KIND:
        return any(dices[i] >= 4 for i in range(6))

    elif category == FULL_HOUSE:
        return 2 in dices and 3 in dices

    elif category == CHANCE:
        return True

    elif category == YAHTZEE:
        return 5 in dices

    else:
        logger.error(f"Invalid Category passed to moveFitsReq function: {category}.")
        return False


def getMoveScore(
    game: Game,
    category: Category,
    dices: Dices,
) -> int:
    """Gets the score of claiming a category."""
    if not moveFitsReq(category, game):
        return 0

    constScore = constScoreCategories[category]
    if constScore is not None:
        return constScore

    elif category <= SIXES:
        return dices[category] * (category + 1)

    # special Yahtzee logic, edit if needed
    elif category == YAHTZEE:
        return (
            100
            if yahtzeeBonus and (game[USED_CATEGORIES_INDEX] >> category) & 1
            else 50
        )

    else:
        return sum(count * (i + 1) for i, count in enumerate(dices))


def claimCategory(
    game: Game,
    category: Category,
    isJoker: bool = False,
) -> tuple[Game, int]:
    """Claim category and update internals. Does not check for validity."""
    upperSectionScore = game[UPPER_SECTION_SCORE_INDEX]

    moveScore = getMoveScore(game, category, game[DICES_INDEX])
    if category <= SIXES:
        previousScore = upperSectionScore
        upperSectionScore += moveScore

        if upperSectionScore >= 63:
            upperSectionScore = 63
            if previousScore < 63:
                moveScore += 35

    yahtzeeDisabled = game[YAHTZEE_DISABLED_INDEX] or (
        category == YAHTZEE and moveScore == 0
    )

    usedCategories = game[USED_CATEGORIES_INDEX] | (1 << category)

    turnsLeft = game[TURNS_LEFT_INDEX]
    if not isJoker:
        turnsLeft -= 1

    # reset turn state
    dices = game[DICES_INDEX]
    rollsLeft = 3

    newGame: Game = (
        turnsLeft,
        usedCategories,
        upperSectionScore,
        dices,
        rollsLeft,
        yahtzeeDisabled,
    )

    return newGame, moveScore


def getLegalClaims(game: Game) -> list[tuple[Category, Category]]:
    """Get a list of legal (possibly zero-score) claims via category indexes."""
    usedCategories = game[USED_CATEGORIES_INDEX]

    categoriesAvailable = [
        (cast(Category, i), NULL)
        for i in range(ONES, YAHTZEE)
        if not ((usedCategories >> i) & 1)
    ]

    if not (usedCategories & (1 << YAHTZEE)):
        categoriesAvailable.append((YAHTZEE, NULL))
    # joker rule
    elif not game[YAHTZEE_DISABLED_INDEX] and 5 in game[DICES_INDEX]:
        availableUpperSectionCategory: Category = game[DICES_INDEX].index(5)

        # prioritize upper section category
        if usedCategories & (1 << availableUpperSectionCategory):
            categoriesAvailable.append((YAHTZEE, availableUpperSectionCategory))
        else:
            # lower section categories
            for category in range(SMALL_STRAIGHT, YAHTZEE):
                categoriesAvailable.append((YAHTZEE, cast(Category, category)))

    return categoriesAvailable


if __name__ == "__main__":
    from yahtzee_init import availableRerolls
    from yahtzee_tests import *

    game = initGameWithDicesAsTuple()
    for dices, category, expected in categoryTests:
        game = (*game[:3], dices, *game[4:])
        if moveFitsReq(globals()[category.upper()], game) != expected:
            print(
                f"Failed category test case: {(category, dices)}: Expected {expected}."
            )

    for dices, expectedCount in rerollGeneratorTests:
        rerollCount = len(availableRerolls[tuple(dices)])
        if rerollCount != expectedCount:
            print(
                f"Failed reroll test case: Expected {expectedCount} but got {rerollCount}."
            )

    for claims, expectedUsed, expectedUpperSectionScore in gameTests:
        game = initGameWithDicesAsTuple()
        for dices, category, expectedScore in claims:
            game = (*game[:3], dices, *game[4:])
            game, claimResult = claimCategory(game, category)
            if claimResult != expectedScore:
                print(
                    f"Failed game claim score test case: Expected {expectedScore} but got {claimResult}."
                )
        if (
            game[USED_CATEGORIES_INDEX] != expectedUsed
            or game[UPPER_SECTION_SCORE_INDEX] != expectedUpperSectionScore
        ):
            print(
                "Failed game result test case: "
                f"Expected used categories {expectedUsed:0>13b} and upper section score {expectedUpperSectionScore}, "
                f"but got used categories {game[USED_CATEGORIES_INDEX]:0>13b} and upper section score {game[UPPER_SECTION_SCORE_INDEX]}."
            )

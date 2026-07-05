import logging
from yahtzee_locals import *
from yahtzee_config import *
from yahtzee_init import *
from typing import TypeAlias

logger = logging.getLogger(__name__)

#use legacy TypeAlias for pre-3.12 pypy
Game: TypeAlias = tuple[int, int, int, Dices, int, bool]
GameWithDiceAsIndex: TypeAlias = tuple[int, int, int, int, int, bool] #dices represented as index
#access indexes
TURNS_LEFT_INDEX = 0
USED_CATEGORIES_INDEX = 1
UPPER_SECTION_SCORE_INDEX = 2
DICES_INDEX = 3
ROLLS_LEFT_INDEX = 4
YAHTZEE_DISABLED_INDEX = 5


def initGame() -> GameWithDiceAsIndex:
    return (
        13, #turnsLeft
        0, #usedCategories
        0, #upperSectionScore
        999, #dices; 999 should raise index out of bounds if access is attempted
        3, #rollsLeft
        false, #yahtzeeDisabled
    )


def moveFitsReq(
        category: Category,
        game: Game,
) -> bool:
    dices = game[DICES_INDEX]
    '''Checks if a category claim fits the requirements of the category.
    Does not check if category has been used.'''
    #big elif block below
    if category <= SIXES:
        return (dices[category] > 0)
    
    elif category == SMALL_STRAIGHT:
        return any(
            all(dices[j] > 0 for j in range(i, i + 4))
            for i in range(3)
        )
    
    elif category == LARGE_STRAIGHT:
        return (dices == (1,1,1,1,1,0) or dices == (0,1,1,1,1,1))
    
    elif category == THREE_OF_A_KIND:
        return any(dices[i] >= 3 for i in range(6))
    
    elif category == FOUR_OF_A_KIND:
        return any(dices[i] >= 4 for i in range(6))
    
    elif category == FULL_HOUSE:
        return (2 in dices and 3 in dices)
    
    elif category == CHANCE:
        return True
    
    elif category == YAHTZEE:
        return (not game[YAHTZEE_DISABLED_INDEX] and 5 in dices)
    
    else:
        logger.error(f"Invalid Category passed to moveFitsReq function: {category}.")
        return False
    

def getMoveScore(
        game: Game,
        category: Category,
        dices: Dices,
) -> int:
    '''Gets the score of claiming a category.'''
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
        return sum(count * (i+1) for i,count in enumerate(dices))
        


def claimCategory(
        game: Game,
        category: Category,
) -> tuple[GameWithDiceAsIndex, int]:
    '''Claim category and update internals. Does not check for validity.'''
    upperSectionScore = game[UPPER_SECTION_SCORE_INDEX]

    moveScore = getMoveScore(game, category, game[DICES_INDEX])
    if category <= SIXES:
        previousScore = upperSectionScore
        upperSectionScore += moveScore
        
        if upperSectionScore >= 63:
            upperSectionScore = 63
            if previousScore < 63:
                moveScore += 35

    yahtzeeDisabled = (
        game[YAHTZEE_DISABLED_INDEX]
        or (category == YAHTZEE and moveScore == 0)
    )

    usedCategories = game[USED_CATEGORIES_INDEX] | (1 << category)
    
    turnsLeft = game[TURNS_LEFT_INDEX] - 1
    #reset turn state
    dicesIndex = 999 #999 should raise index out of bounds if access is attempted
    rollsLeft = 3

    newGame: GameWithDiceAsIndex = (
        turnsLeft,
        usedCategories,
        upperSectionScore,
        dicesIndex,
        rollsLeft,
        yahtzeeDisabled,
    )

    return newGame, moveScore

def getLegalClaims(game: Game) -> list[int]:
    '''Get a list of legal (possibly zero-score) claims via category indexes.'''
    categoriesAvailable = [i for i in range(ONES, YAHTZEE) if not ((game[USED_CATEGORIES_INDEX] >> i) & 1)]
    categoriesAvailable.append(YAHTZEE) #yahtzee can be scored multiple times
    return categoriesAvailable
    
    
if __name__ == "__main__":
    from yahtzee_init import availableRerolls
    from yahtzee_tests import *
    
    game = initGame()
    for dices,category,expected in categoryTests:
        if moveFitsReq(globals()[category.upper()], dices) != expected:
            print(f"Failed category test case: {(category, dices)}: Expected {expected}.")

    for dices,expectedCount in rerollGeneratorTests:
        rerollCount = len(availableRerolls[tuple(dices)])
        if rerollCount != expectedCount:
            print(f"Failed reroll test case: Expected {expectedCount} but got {rerollCount}.")
    
    for claims,expectedUsed,expectedUpperSectionScore in gameTests:
        game = initGame()
        for dices,category,expectedScore in claims:
            game = (*game[:3], dices, game[4])
            game, claimResult = claimCategory(game, category)
            if claimResult != expectedScore:
                print(f"Failed game claim score test case: Expected {expectedScore} but got {claimResult}.")
        if (
            game[USED_CATEGORIES_INDEX] != expectedUsed
            or game[UPPER_SECTION_SCORE_INDEX] != expectedUpperSectionScore
        ):
            print(f"Failed game result test case: Expected used categories {expectedUsed} and upper section score {expectedUpperSectionScore}.")

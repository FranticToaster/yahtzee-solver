import logging
from math import prod
from itertools import product, combinations_with_replacement
from yahtzee_locals import *
from yahtzee_config import *

logger = logging.getLogger(__name__)


factorials = [1, 1, 2, 6, 24, 120, 720]


def precomputeRollOutcomes() -> list[list[tuple[Dices, int]]]:
    table = []

    for i in range(6):
        row = []
        for combination in combinations_with_replacement(range(6), i):
            #convert to Dices format (counts of each value)
            dices = [0] * 6
            for value in combination:
                dices[value] += 1

            #number of different permutations of the same combination
            permutations = factorials[i] / prod(factorials[e] for e in dices)

            probability = permutations * prod(dieWeights[value]/dieWeightsSum for value in combination)
            row.append((dices,probability))
        table.append(row)

    return table

#pretty messy but not much time is available to clean up code
class Game:
    #idk why i made this a class attribute instead of global var
    rollOutcomes = precomputeRollOutcomes()
    def __init__(
            self,
            *_,
    ) -> None:
        self.turnsLeft = 13

        # game state
        #usedCategories is a bitmask that starts from the right, i.e. the rightmost bit is category index 0
        self.usedCategories = 0
        self.upperSectionScore = 0

        # turn state
        #dice numbers shall be 1-indexed
        #dices will be represented as counts of each value e.g. [3,2,0,0,0,0] would mean 3 '1's and 2 '2's
        self.dices = [0] * 6
        self.rollsLeft = 3

    def __hash__ (self) -> int:
        hash_ = self.turnsLeft
        hash_ <<= 13
        hash_ += self.usedCategories
        hash_ <<= 6
        hash_ += self.upperSectionScore
        #5**6 = 15625 fits in 14 bits
        hash_ <<= 14
        hash_ += sum((5**i) * e for i,e in enumerate(self.dices))
        hash_ <<= 2
        hash_ += self.rollsLeft
        return hash_

    def copy(self):
        game = Game()
        game.turnsLeft = self.turnsLeft

        game.usedCategories = self.usedCategories
        game.upperSectionScore = self.upperSectionScore

        game.dices = self.dices.copy()
        game.rollsLeft = self.rollsLeft
        return game

    def moveFitsReq(
            self,
            category: Category,
            dices: Dices,
    ) -> bool:
        '''Checks if a category claim fits the requirements of the category.
        Does not check if category has been used.'''
        #big elif block below
        if ONES <= category <= SIXES:
            return (dices[category] > 0)
        
        elif category == SMALL_STRAIGHT:
            return any(
                all(dices[j] > 0 for j in range(i, i + 4))
                for i in range(2)
            )
        
        elif category == LARGE_STRAIGHT:
            return (dices == [1,1,1,1,1,0] or dices == [0,1,1,1,1,1])
        
        elif category == THREE_OF_A_KIND:
            return any(dices[i] >= 3 for i in range(6))
        
        elif category == FOUR_OF_A_KIND:
            return any(dices[i] >= 4 for i in range(6))
        
        elif category == FULL_HOUSE:
            return (2 in dices and 3 in dices)
        
        elif category == CHANCE:
            return True
        
        elif category == YAHTZEE:
            return (5 in dices)
        
        else:
            logger.error(f"Invalid Category passed to moveFitsReq function: {category}.")
            return False
        

    def getMoveScore(
            self,
            category: Category,
            dices: Dices,
    ) -> int:
        '''Gets the score of claiming a category.'''
        if not self.moveFitsReq(category, dices):
            return 0
        
        constScore = constScoreCategories[category]
        if constScore is not None:
            return constScore
        
        elif ONES <= category <= SIXES:
            return dices[category] * (category + 1)
        
        # special Yahtzee logic, edit if needed
        elif category == YAHTZEE:
            return (
                100
                if yahtzeeBonus and (self.usedCategories >> category) & 1
                else 50
            )

        else:
            return sum(count * (i+1) for i,count in enumerate(self.dices))
            

    def claimRoll(
            self,
            dices: Dices,
    ) -> None:
        '''Attempts to claim a roll result and updates internals accordingly.'''
        if self.rollsLeft == 0:
            logger.error("Attempted to claim roll result with 0 rolls left in turn.")
            return
        self.dices = dices

    def getRerolls(self):
        '''Generator for possible rerolls.'''
        # ranges of possible reroll counts for each face.
        # e.g. if i have 3 '1's i can reroll 0, 1, 2 or 3 i.e. range(3 + 1) dices
        ranges = [range(self.dices[face] + 1) for face in range(6)]
        return product(*ranges)
    

    def claimCategory(
            self,
            category: Category,
    ) -> int:
        '''Attempt to claim a category and update internals accordingly. Returns score of claim or 0 if an error occurs.'''
        if not (ONES <= category <= YAHTZEE):
            logger.error(f"Invalid category index: {category}!")
            return 0

        if (
            category != YAHTZEE
            and ((self.usedCategories >> category) & 1)
        ):
            logger.error(f"Category {category} has already been used! Used categories bitmask: {self.usedCategories}.")
            return 0

        moveScore = self.getMoveScore(category, self.dices)
        if category <= SIXES and self.upperSectionScore < 63:
            self.upperSectionScore = max(
                63,
                self.upperSectionScore + moveScore
            )
        

        self.usedCategories |= (1 << category)
        
        self.turnsLeft -= 1
        #reset turn state
        self.dices = [0] * 6
        self.rollsLeft = 3

        return moveScore

    def getLegalClaims(self) -> list[int]:
        '''Get a list of legal (possibly zero-score) claims via category indexes.'''
        categoriesAvailable = [i for i in range(ONES, YAHTZEE) if not ((self.usedCategories >> i) & 1)]
        categoriesAvailable.append(YAHTZEE) #yahtzee can be scored multiple times
        return categoriesAvailable
    
    
if __name__ == "__main__":
    from yahtzee_tests import *
    game = Game()
    for dices,category,expected in categoryTests:
        if game.moveFitsReq(globals()[category.upper()], list(dices)) != expected:
            print(f"Failed category test case: {(category, dices)}: Expected {expected}.")

    for dices,expectedCount in rerollGeneratorTests:
        game.dices = list(dices)
        rerollCount = len(list(game.getRerolls()))
        if rerollCount != expectedCount:
            print(f"Failed reroll test case: Expected {expectedCount} but got {rerollCount}.")
    
    for claims,expectedUsed,expectedUpperSectionScore in gameTests:
        game = Game()
        for dices,category,expectedScore in claims:
            game.dices = list(dices)
            claimResult = game.claimCategory(category)
            if claimResult != expectedScore:
                print(f"Failed game claim score test case: Expected {expectedScore} but got {claimResult}.")
        if game.usedCategories != expectedUsed or game.upperSectionScore != expectedUpperSectionScore:
            print(f"Failed game result test case: Expected used categories {expectedUsed} and upper section score {expectedUpperSectionScore}.")

import logging
import os

DIR_PATH = os.path.dirname(os.path.abspath(__file__))

logger = logging.getLogger(__name__)
logging.basicConfig(
    filename = os.path.join(DIR_PATH, f"searchLog.log"),
    filemode = "w",
    format = "%(asctime)s [%(levelname)s] %(filename)s: %(message)s",
    datefmt = "%Y-%m-%d %H:%M:%S",
    level = logging.INFO,
)

import line_profiler
from functools import cache
from yahtzee_game import *
from yahtzee_init import *



#metrics
leaf_nodes_evaluated = 0
total_nodes_evaluated = 0


@cache
#idk how to make this conditional so just comment it out for now
#@line_profiler.profile
# use gameInt (bitpacked) instead of separate args for faster caching
#TODO: ensure sum=5 dice combinations fit within 256
def dfs(gameInt: GameAsInt) -> float:
    global total_nodes_evaluated, leaf_nodes_evaluated
    total_nodes_evaluated += 1
    
    turnsLeft = (gameInt >> 2) & 0b1111

    if turnsLeft == 0:
        leaf_nodes_evaluated += 1
        return 0
    
    usedCategories = (gameInt >> 20)
    upperSectionScore = (gameInt >> 6) & 0b111111
    rollsLeft = gameInt & 0b11

    # we handle this case first since we cannot claim immediately at the start of the turn, 
    # so in this case we will skip the claim best score calculation
    if rollsLeft == 3:
        score = 0
        for rollResultIdx, probability in rollOutcomesByIdx[5]:
            score += probability * dfs(
                (turnsLeft << 2)
                | (usedCategories << 20)
                | (upperSectionScore << 6)
                | (rollResultIdx << 12)
                | 2 #rollsLeft - 1 == 2 when rollsLeft == 3
            )
        return score
    
    dicesIndex = (gameInt >> 12) & 0b11111111
    dicesValue = idxToDices[dicesIndex]
    game = (turnsLeft, usedCategories, upperSectionScore, dicesValue, rollsLeft)

    # calculate claim first since we can choose to claim at any point in time 
    # as long as its not the start of the turn, which we already accounted for previously
    best_score = -1.0
    for category in getLegalClaims(game):
        gameCopy, claimedScore = claimCategory(game, category)
        score = claimedScore + dfs(
            (gameCopy[0] << 2)
            | (gameCopy[1] << 20)
            | (gameCopy[2] << 6)
            | (gameCopy[3] << 12)
            | gameCopy[4]
        )

        if score > best_score:
            best_score = score


    if rollsLeft == 0:
        # if no rolls left we must claim a category
        return best_score
    
    else:
        rollsLeftMinusOne = rollsLeft - 1
        #average score of rerolls
        for reroll in availableRerolls[dicesValue]:
            rerollOutcomes = rollOutcomesByIdx[sum(reroll)]
            remainingDicesIdx = dicesToIdx[tuple(x - y for x,y in zip(dicesValue, reroll))]

            score = 0.0
            for rollResultIdx, probability in rerollOutcomes:
                score += probability * dfs(
                    (turnsLeft << 2)
                    | (usedCategories << 20)
                    | (upperSectionScore << 6)
                    | (dicesAdditionByIdx[remainingDicesIdx][rollResultIdx] << 12)
                    | rollsLeftMinusOne
                )
            

            if score > best_score:
                best_score = score
        
        return best_score


if __name__ == "__main__":
    from time import perf_counter

    start_time = perf_counter()
    result = dfs(initGame())
    end_time = perf_counter()

    logger.info(f"Searched {leaf_nodes_evaluated} leaf nodes and {total_nodes_evaluated} total nodes (excluding cache).")
    logger.info(f"Cache info: {dfs.cache_info()}.")
    logger.info(f"Took {end_time - start_time}s.")
    logger.info(f"Best score found: {result}.")

    

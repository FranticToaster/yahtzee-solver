import logging
import os
from datetime import datetime

DIR_PATH = os.path.dirname(os.path.abspath(__file__))

logger = logging.getLogger(__name__)
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
logging.basicConfig(
    filename=os.path.join(DIR_PATH, f"search_log_{timestamp}.log"),
    filemode="w",
    format="%(asctime)s [%(levelname)s] %(filename)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)

# import line_profiler #unsupported by pypy
from functools import cache
from yahtzee_game import *
from yahtzee_init import *

# metrics
leaf_nodes_evaluated = 0
total_nodes_evaluated = 0


@cache
# idk how to make this conditional so just comment it out for now
# @line_profiler.profile
# use separate args instead of packing into Game obj for better caching
def dfs(
    turnsLeft: int,
    usedCategories: int,
    upperSectionScore: int,
    dicesIndex: int,
    rollsLeft: int,
    yahtzeeDisabled: bool,
) -> float:
    global total_nodes_evaluated, leaf_nodes_evaluated
    total_nodes_evaluated += 1

    if turnsLeft == 0:
        leaf_nodes_evaluated += 1
        return 0

    # we handle this case first since we cannot claim immediately at the start of the turn,
    # so in this case we will skip the claim best score calculation
    if rollsLeft == 3:
        score = 0
        for rollResultIdx, probability in rollOutcomesByIdx[5]:
            score += probability * dfs(
                turnsLeft,
                usedCategories,
                upperSectionScore,
                rollResultIdx,
                2,  # rollsLeft - 1 == 2 when rollsLeft == 3
                yahtzeeDisabled,
            )
        return score

    dicesValue = idxToDices[dicesIndex]
    game = (
        turnsLeft,
        usedCategories,
        upperSectionScore,
        dicesValue,
        rollsLeft,
        yahtzeeDisabled,
    )

    # calculate claim first since we can choose to claim at any point in time
    # as long as its not the start of the turn, which we already accounted for previously
    best_score = -1.0
    for category in getLegalClaims(game):
        gameCopy, claimedScore = claimCategory(game, category[0])
        gameCopy, jokerBonus = claimCategory(gameCopy, category[1])

        score = claimedScore + jokerBonus + dfs(*gameCopy)

        if score > best_score:
            best_score = score

    if rollsLeft == 0:
        # if no rolls left we must claim a category
        return best_score

    else:
        rollsLeftMinusOne = rollsLeft - 1
        # average score of rerolls
        for reroll in availableRerolls[dicesValue]:
            rerollOutcomes = rollOutcomesByIdx[sum(reroll)]
            remainingDicesIdx = dicesToIdx[
                tuple(x - y for x, y in zip(dicesValue, reroll))
            ]

            score = 0.0
            for rollResultIdx, probability in rerollOutcomes:
                score += probability * dfs(
                    turnsLeft,
                    usedCategories,
                    upperSectionScore,
                    dicesAdditionByIdx[remainingDicesIdx][rollResultIdx],
                    rollsLeftMinusOne,
                    yahtzeeDisabled,
                )

            if score > best_score:
                best_score = score

        return best_score


if __name__ == "__main__":
    from time import perf_counter

    start_time = perf_counter()
    result = dfs(*initGame())
    end_time = perf_counter()

    logger.info(
        f"Searched {leaf_nodes_evaluated} leaf nodes and {total_nodes_evaluated} total nodes (excluding cache)."
    )
    logger.info(f"Cache info: {dfs.cache_info()}.")
    logger.info(f"Took {end_time - start_time}s.")
    logger.info(f"Best score found: {result}.")

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

from functools import cache
from yahtzee_game import *
from yahtzee_init import *



#metrics
leaf_nodes_evaluated = 0
total_nodes_evaluated = 0


# use separate args instead of packing into Game obj for better caching
@cache
def dfs(
    turnsLeft: int,
    usedCategories: int,
    upperSectionScore: int,
    dicesIndex: int,
    rollsLeft: int,
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
        for rollResult, probability in rollOutcomes[5]:
            gameCopy = (
                turnsLeft,
                usedCategories,
                upperSectionScore,
                dicesToIdx[rollResult],
                rollsLeft - 1
            )
            score += dfs(*gameCopy) * probability
        return score
    
    dicesValue = idxToDices[dicesIndex]
    game = (turnsLeft, usedCategories, upperSectionScore, dicesValue, rollsLeft)

    # calculate claim first since we can choose to claim at any point in time 
    # as long as its not the start of the turn, which we already accounted for previously
    best_score = -1
    for category in getLegalClaims(game):
        gameCopy, claimedScore = claimCategory(game, category)
        score = claimedScore + dfs(*gameCopy)
        best_score = max(best_score, score)


    if rollsLeft == 0:
        # if no rolls left we must claim a category
        return best_score
    
    else:
        #average score of rerolls
        for reroll in availableRerolls[tuple(game[DICES_INDEX])]:
            numRolled = sum(reroll)
            score = 0
            remainingDices = [x - y for x,y in zip(game[DICES_INDEX], reroll)]
            for rollResult, probability in rollOutcomes[numRolled]:
                # ugly but around 2x faster
                newDices = (
                    remainingDices[0] + rollResult[0],
                    remainingDices[1] + rollResult[1],
                    remainingDices[2] + rollResult[2],
                    remainingDices[3] + rollResult[3],
                    remainingDices[4] + rollResult[4],
                    remainingDices[5] + rollResult[5],
                )
                gameCopy = (
                    turnsLeft,
                    usedCategories,
                    upperSectionScore,
                    dicesToIdx[newDices],
                    rollsLeft - 1,
                )
                score += dfs(*gameCopy) * probability
            best_score = max(best_score, score)
        
        return best_score


if __name__ == "__main__":
    import cProfile
    import pstats
    import io
    from time import perf_counter

    profiling = False

    if profiling:
        profiler = cProfile.Profile()
        profiler.enable()

    start_time = perf_counter()
    result = dfs(*initGame())
    end_time = perf_counter()

    logger.info(f"Searched {leaf_nodes_evaluated} leaf nodes and {total_nodes_evaluated} total nodes (excluding cache).")
    logger.info(f"Cache info: {dfs.cache_info()}.")
    logger.info(f"Took {end_time - start_time}s.")
    logger.info(f"Best score found: {result}.")

    if profiling:
        profiler.disable() #pyright: ignore[reportPossiblyUnboundVariable]
        stream = io.StringIO()
        stats = pstats.Stats(profiler, stream = stream) #pyright: ignore[reportPossiblyUnboundVariable]
        stats.strip_dirs().sort_stats(pstats.SortKey.CUMULATIVE).print_stats(10)

        logger.info(f"\n{stream.getvalue()}")
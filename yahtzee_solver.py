import logging
import os
from functools import cache
from yahtzee_game import *
from yahtzee_init import rollOutcomes, availableRerolls

DIR_PATH = os.path.dirname(os.path.abspath(__file__))

logger = logging.getLogger(__name__)
logging.basicConfig(
    filename = os.path.join(DIR_PATH, f"searchLog.log"),
    filemode = "w",
    format = "%(asctime)s [%(levelname)s] %(filename)s: %(message)s",
    datefmt = "%Y-%m-%d %H:%M:%S",
    level = logging.INFO,
)

#metrics
leaf_nodes_evaluated = 0
total_nodes_evaluated = 0


@cache
def dfs(
    game: Game,
) -> float:
    global total_nodes_evaluated, leaf_nodes_evaluated
    total_nodes_evaluated += 1

    if game.turnsLeft == 0:
        leaf_nodes_evaluated += 1
        return 0

    # we handle this case first since we cannot claim immediately at the start of the turn, 
    # so in this case we will skip the claim best score calculation
    if game.rollsLeft == 3:
        score = 0
        for dices, probability in rollOutcomes[5]:
            gameCopy = game.copy()
            gameCopy.claimRoll(dices)
            score += dfs(gameCopy) * probability
        return score
    

    # calculate claim first since we can choose to claim at any point in time 
    # as long as its not the start of the turn, which we already accounted for previously
    best_score = -1
    for category in game.getLegalClaims():
        gameCopy = game.copy()
        claimedScore = gameCopy.claimCategory(category)
        score = claimedScore + dfs(gameCopy)
        best_score = max(best_score, score)


    if game.rollsLeft == 0:
        # if no rolls left we must claim a category
        return best_score
    
    else:
        #average score of rerolls
        for reroll in availableRerolls[tuple(game.dices)]:
            numRolled = sum(reroll)
            score = 0
            remainingDices = [x - y for x,y in zip(game.dices, reroll)]
            for dices, probability in rollOutcomes[numRolled]:
                gameCopy = game.copy()
                newDices = [x + y for x,y in zip (remainingDices, dices)]
                gameCopy.claimRoll(newDices)
                score += dfs(gameCopy) * probability
            best_score = max(best_score, score)
        
        return best_score


if __name__ == "__main__":
    from time import perf_counter
    game = Game()
    start_time = perf_counter()
    result = dfs(game)
    end_time = perf_counter()
    logger.info(f"Searched {leaf_nodes_evaluated} leaf nodes and {total_nodes_evaluated} total nodes.")
    logger.info(f"Cache info: {dfs.cache_info()}.")
    logger.info(f"Took {end_time - start_time}s.")
    logger.info(f"Best score found: {result}.")
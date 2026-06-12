import logging
import os
from yahtzee_game import *

DIR_PATH = os.path.dirname(os.path.abspath(__file__))

logger = logging.getLogger(__name__)
logging.basicConfig(
    filename = os.path.join(DIR_PATH, f"searchLog.log"),
    filemode = "w",
    format = "%(asctime)s [%(levelname)s] %(filename)s: %(message)s",
    datefmt = "%Y-%m-%d %H:%M:%S",
)

#metrics
leaf_nodes_evaluated = 0
total_nodes_evaluated = 0


cache: dict[Game, int] = {}

def dfs(
    game: Game,
) -> int:
    global total_nodes_evaluated, leaf_nodes_evaluated
    total_nodes_evaluated += 1

    if game.turnsLeft == 0:
        leaf_nodes_evaluated += 1
        return 0
    
    cachedResult = cache.get(game, None)
    if cachedResult is not None:
        return cachedResult
    

    # we handle this case first since we cannot claim immediately at the start of the turn, 
    # so in this case we will skip the claim best score calculation
    if game.rollsLeft == 3:
        score = 0
        for dices, probability in Game.rollOutcomes[5]:
            gameCopy = game.copy()
            gameCopy.claimRoll(dices)
            score += dfs(gameCopy) * probability
        cache[game] = score
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
        cache[game] = best_score
        return best_score
    
    else:
        #average score of rerolls
        for reroll in game.getRerolls():
            numRolled = sum(reroll)
            score = 0
            for dices, probability in Game.rollOutcomes[numRolled]:
                gameCopy = game.copy()
                gameCopy.claimRoll(dices)
                score += dfs(gameCopy) * probability
            best_score = max(best_score, score)
        
        cache[game] = best_score
        return best_score
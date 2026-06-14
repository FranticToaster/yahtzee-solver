import logging
from time import perf_counter
from math import prod
from itertools import product, combinations_with_replacement
from yahtzee_locals import Dices
from yahtzee_config import dieWeights, dieWeightsSum


logger = logging.getLogger(__name__)
start_time = perf_counter()
logger.info("Initialization started.")

factorials = [1, 1, 2, 6, 24, 120, 720]

#quite a bit of repetition but its precomputed so not a big deal
def precomputeRollOutcomesByIdx(dicesToIdx) -> list[list[tuple[int, float]]]:
    table = []

    for i in range(6):
        row = []
        for combination in combinations_with_replacement(range(6), i):
            #convert to Dices format (counts of each value)
            dices = [0] * 6
            for value in combination:
                dices[value] += 1
            dices = tuple(dices)
            dicesIdx = dicesToIdx[dices]

            #number of different permutations of the same combination
            permutations = factorials[i] // prod(factorials[e] for e in dices)

            probability = permutations * prod(dieWeights[value]/dieWeightsSum for value in combination)
            row.append((dicesIdx,probability))
        table.append(row)

    return table


def precomputeAvailableRerolls() -> dict[Dices, list[Dices]]:
    table = {}
    for combination in combinations_with_replacement(range(6), 5):
        dices = [0] * 6
        for value in combination:
            dices[value] += 1
        dices = tuple(dices)
        
        # ranges of possible reroll counts for each face.
        # e.g. if i have 3 '1's i can reroll 0, 1, 2 or 3 i.e. range(3 + 1) dices
        ranges = [range(dices[face] + 1) for face in range(6)]
        availableRerolls = tuple(product(*ranges))
        table[dices] = availableRerolls
    return table



def precomputeDiceIndexes() -> tuple[dict[Dices, int], list[Dices]]:
    dicesToIdx = {}
    idxToDices = []
    index = 0
    for i in range(6):
        for combination in combinations_with_replacement(range(6), i):
            dices = [0] * 6
            for value in combination:
                dices[value] += 1
            dices = tuple(dices)
            
            dicesToIdx[dices] = index
            idxToDices.append(dices)
            index += 1
            
    return dicesToIdx, idxToDices



def precomputeDicesAdditionByIdx(dicesToIdx,idxToDices) -> list[list[int]]:
    table = []
    for i in range(462):
        row = []

        dices_i = idxToDices[i]
        for j in range(462):
            dices_j = idxToDices[j]

            newDices = tuple(x + y for x,y in zip(dices_i, dices_j))
            if sum(newDices) > 5:
                continue

            row.append(dicesToIdx[newDices])

        table.append(row)
    return table
    

dicesToIdx, idxToDices = precomputeDiceIndexes()
rollOutcomesByIdx = precomputeRollOutcomesByIdx(dicesToIdx)
availableRerolls = precomputeAvailableRerolls()
dicesAdditionByIdx = precomputeDicesAdditionByIdx(dicesToIdx, idxToDices)




logger.info("Initialization complete.")
time_taken = perf_counter() - start_time
logger.info(f"Precomputation took a total of {time_taken}s.")
if time_taken > 5:
    logger.warning("Precomputation took more than 5s!")
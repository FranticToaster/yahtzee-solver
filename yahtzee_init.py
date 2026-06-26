__all__ = [
    "dicesToIdx",
    "idxToDices",
    "rollOutcomesByIdx",
    "availableRerolls",
    "dicesAdditionByIdx",
]

import logging
from sys import version
from time import perf_counter
from math import prod
from itertools import product, combinations_with_replacement
from yahtzee_locals import Dices
from yahtzee_config import dieWeights, dieWeightsSum


_logger = logging.getLogger(__name__)
_logger.info(f"VERSION {version}")
_start_time = perf_counter()
_logger.info("Initialization started.")

_factorials = [1, 1, 2, 6, 24, 120, 720]

#quite a bit of repetition but its precomputed so not a big deal
def _precomputeRollOutcomesByIdx(dicesToIdx) -> list[list[tuple[int, float]]]:
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
            permutations = _factorials[i] // prod(_factorials[e] for e in dices)

            probability = permutations * prod(dieWeights[value]/dieWeightsSum for value in combination)
            row.append((dicesIdx,probability))
        table.append(row)

    return table


def _precomputeAvailableRerolls() -> dict[Dices, list[Dices]]:
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



def _precomputeDiceIndexes() -> tuple[dict[Dices, int], list[Dices]]:
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



def _precomputeDicesAdditionByIdx(dicesToIdx,idxToDices) -> list[list[int]]:
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
    

dicesToIdx, idxToDices = _precomputeDiceIndexes()
rollOutcomesByIdx = _precomputeRollOutcomesByIdx(dicesToIdx)
availableRerolls = _precomputeAvailableRerolls()
dicesAdditionByIdx = _precomputeDicesAdditionByIdx(dicesToIdx, idxToDices)




_logger.info("Initialization complete.")
_time_taken = perf_counter() - _start_time
_logger.info(f"Precomputation took a total of {_time_taken}s.")
if _time_taken > 5:
    _logger.warning("Precomputation took more than 5s!")

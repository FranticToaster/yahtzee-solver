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
def precomputeRollOutcomes() -> list[list[tuple[Dices, float]]]:
    table = []

    for i in range(6):
        row = []
        for combination in combinations_with_replacement(range(6), i):
            #convert to Dices format (counts of each value)
            dices = [0] * 6
            for value in combination:
                dices[value] += 1

            #number of different permutations of the same combination
            permutations = factorials[i] // prod(factorials[e] for e in dices)

            probability = permutations * prod(dieWeights[value]/dieWeightsSum for value in combination)
            row.append((tuple(dices),probability))
        table.append(row)

    return table

def precomputeAvailableRerolls() -> dict[Dices, list[Dices]]:
    table = {}
    for combination in combinations_with_replacement(range(6), 5):
        dices = [0] * 6
        for value in combination:
            dices[value] += 1
        
        # ranges of possible reroll counts for each face.
        # e.g. if i have 3 '1's i can reroll 0, 1, 2 or 3 i.e. range(3 + 1) dices
        ranges = [range(dices[face] + 1) for face in range(6)]
        availableRerolls = tuple(product(*ranges))
        table[tuple(dices)] = availableRerolls
    return table


rollOutcomes = precomputeRollOutcomes()
availableRerolls = precomputeAvailableRerolls()

logger.info("Initialization complete.")
time_taken = perf_counter() - start_time
logger.info(f"Precomputation took a total of {time_taken}s.")
if time_taken > 0.5:
    logger.warning("Precomputation took more than 0.5s!")
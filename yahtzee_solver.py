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


cache = []

def dfs(
    game: Game,
) -> int:
    if game.turnsLeft == 0:
        return 0
    #TODO, complete solver
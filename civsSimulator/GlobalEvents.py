import random
from civsSimulator import Utils
import math

# ================================================
# ====     Helper functions for the events    ====
# ================================================


def famine_in_turn():
    if random.random() < 0.3:
        if random.random() < 0.3:
            if random.random() < 0.2:
                return True
    return False


# =======================
# ====     Events    ====
# =======================


def famine(world, information, verbose):
    if famine_in_turn():
        for g in information["groups"]:
            if g.prosperity < 0.4 and not g.is_dead:
                g.kill()
                fact = "{} has dead of famine".format(g.name)
                if verbose:
                    if information["turn"] in g.facts:
                        g.facts[information["turn"]].append(fact)
                    else:
                        g.facts[information["turn"]] = [fact]

import random
from civsSimulator import Utils
import math


def discovery_population_factor(total, required):
    return math.log10(total / required) + 1


def chance_to_become_semi_sedentary(group):
    prosperity = group.prosperity
    if group.nomadism == "nomadic" and prosperity > 0.6:
        return Utils.saturate((prosperity - 0.75) / 1.5, 0.1)
    else:
        return 0


def chance_to_discover_agriculture(group, world):
    if group.nomadism != "nomadic" and not ("Agriculture" in group.activities):
        agr_prosp = group.get_base_prosperity_per_activity("Agriculture", world, group.position)
        p = (agr_prosp - 0.75) * 6.0
        p *= discovery_population_factor(group.total_persons, 200)
        return Utils.saturate(max(0.0, p), 0.3)
    else:
        return 0


def chance_to_become_sedentary(group):
    if group.nomadism == "semi-sedentary" and "Agriculture" in group.activities:
        prosperity = group.prosperity
        if prosperity > 0.72:
            return Utils.saturate((prosperity - 0.75) / 1.5, 0.2)
        else:
            return 0
    else:
        return 0


# Events
def become_semi_sedentary(group, world):
    if random.random() < chance_to_become_semi_sedentary(group):
        group.nomadism = "semi-sedentary"


def discover_agriculture(group, world):
    if random.random() < chance_to_discover_agriculture(group, world):
        group.activities.append("Agriculture")


def become_sedentary(group, world):
    if random.random() < chance_to_become_sedentary(group):
        group.nomadism = "sedentary"


def migrate(group, world):
    pass

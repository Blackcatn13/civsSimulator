import random
from civsSimulator import Utils
import math
import itertools

# ================================================
# ====     Helper functions for the events    ====
# ================================================


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


def inside_world(world, pos):
    return 0 < pos[0] < world.width and 0 < pos[1] < world.height


def is_land(world, pos):
    return world.biome_at(pos).name() != "ocean"


def land_cells_around(world, pos, radius, occupied_positions):
    rad = range(-radius, radius+1)
    positions = itertools.product(rad, rad)
    filtered = (Utils.add_list(pos, p) for p in positions if inside_world(world, Utils.add_list(pos, p)))
    land = (p for p in filtered if is_land(world, p))
    return (p for p in land if p not in occupied_positions)


class _exhausted:
    pass


def chance_to_migrate(group, world, occupied_positions):
    positions = land_cells_around(world, group.position, group.migration_radius, occupied_positions)
    if next(positions, _exhausted) == _exhausted:
        return 0
    else:
        return (1 - group.prosperity) * group.migration_rate

# =======================
# ====     Events    ====
# =======================


def become_semi_sedentary(group, world, information):
    """
    This event checks if a group can evolve to semi sedentary.

    If the event occurs a fact is added to the group.

    :param group: The group to check.
    :param world: The world.
    :param information: A dictionary with the information for the events.
    """
    if random.random() < chance_to_become_semi_sedentary(group):
        group.facts.append("Group is converting to semi-sedentarism in turn: {}".format(information["turn"]))
        group.nomadism = "semi-sedentary"


def discover_agriculture(group, world, information):
    """
    This event checks if a group discovers agriculture.

    If the event occurs a fact is added to the group.

    :param group: The group to check.
    :param world: The world.
    :param information: A dictionary with the information for the events.
    """
    if random.random() < chance_to_discover_agriculture(group, world):
        group.facts.append("Group has discovered agriculture in turn: {}".format(information["turn"]))
        group.activities.append("Agriculture")


def become_sedentary(group, world, information):
    """
    This event checks if a group can evolve to sedentary.

    If the event occurs a fact is added to the group.

    :param group: The group to check.
    :param world: The world.
    :param information: A dictionary with the information for the events.
    """
    if random.random() < chance_to_become_sedentary(group):
        group.facts.append("Group is converting to sedentarism in turn: {}".format(information["turn"]))
        group.nomadism = "sedentary"


def migrate(group, world, information):
    """
    This event checks if a group migrates from it's current position.

    If the event occurs a fact is added to the group.

    :param group: The group to check.
    :param world: The world.
    :param information: A dictionary with the information for the events.
    """
    if random.random() < chance_to_migrate(group, world, information["occupied_positions"]):
        positions = land_cells_around(world, group.position, group.migration_radius, information["occupied_positions"])
        prosperity = ([Utils.perturbate_low(group.get_prosperity(world, p)), p] for p in positions)
        best = max(prosperity)
        group.facts.append("Group is moving to better lands {} in turn: {}".format(best[1], information["turn"]))
        group.position = best[1]


def dead(group, world, information):
    """
    This event checks if a group is dead.

    If the event occurs a fact is added to the group.

    :param group: The group to check.
    :param world: The world.
    :param information: A dictionary with the information for the events.
    """
    if group.is_dead:
        group.facts.append("Group has dead in turn: {}".format(information["turn"]))


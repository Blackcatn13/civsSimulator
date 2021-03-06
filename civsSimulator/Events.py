import random
from civsSimulator import Utils
import math
import itertools

# ================================================
# ====     Helper functions for the events    ====
# ================================================


def discovery_population_factor(total, required):
    if total == 0:
        return 0
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
    rad = range(-radius, radius + 1)
    positions = itertools.product(rad, rad)
    filtered = (Utils.add_list(pos, p) for p in positions if inside_world(world, Utils.add_list(pos, p)))
    land = (p for p in filtered if is_land(world, p))
    return (p for p in land if p not in occupied_positions)


def groups_around(pos, radius, occupied_positions):
    rad = range(-radius, radius + 1)
    positions = itertools.product(rad, rad)
    return len([p for p in positions if Utils.add_list(pos, p) in occupied_positions and not p == (0, 0)])


def groups_around_info(pos, radius, groups):
    rad = range(-radius, radius + 1)
    positions = itertools.product(rad, rad)
    occupied = [g.position for g in groups]
    g_positions = [Utils.add_list(pos, p) for p in positions if Utils.add_list(pos, p) in occupied and not p == (0, 0)]
    return [g for g in groups if g.position in g_positions]


class _exhausted:
    pass


def chance_to_migrate(group, world, occupied_positions):
    positions = land_cells_around(world, group.position, group.migration_radius, occupied_positions)
    if next(positions, _exhausted) == _exhausted:
        return 0
    else:
        return (1 - group.prosperity) * group.migration_rate


def chance_to_develop_trade(group, occupied_positions):
    if group.nomadism == "sedentary" and not group.knows_trade:
        neighbours = groups_around(group.position, group.trade_radius, occupied_positions)
        if neighbours > 0:
            prosperity = group.prosperity
            if prosperity > 0.8:
                return Utils.saturate((prosperity - 0.78) / 1.3, 0.3)
            else:
                return 0.05
        else:
            return 0
    else:
        return 0


def chance_to_trade(group, information):
    if group.knows_trade:
        neighbours = groups_around_info(group.position, group.trade_radius, information["groups"])
        chance = Utils.saturate(len(neighbours) / (group.trade_radius * group.trade_radius - 1), 0.8)
        return [chance, neighbours]
    return [0, 0]

# =======================
# ====     Events    ====
# =======================


def become_semi_sedentary(group, world, information, verbose):
    """
    This event checks if a group can evolve to semi sedentary.

    If the event occurs a fact is added to the group.

    :param group: The group to check.
    :param world: The world.
    :param information: A dictionary with the information for the events.
    :param verbose: True if the event has to register into facts, False otherwise
    """
    if random.random() < chance_to_become_semi_sedentary(group):
        group.nomadism = "semi-sedentary"
        fact = "{} is converting to semi-sedentarism.".format(group.name)
        if verbose:
            if information["turn"] in group.facts:
                group.facts[information["turn"]].append(fact)
            else:
                group.facts[information["turn"]] = [fact]
        if information["turn"] in group.file_facts:
            group.file_facts[information["turn"]]['nomadism'] = 'semi-sedentary'
        else:
            group.file_facts[information["turn"]] = {'nomadism': 'semi-sedentary'}


def discover_agriculture(group, world, information, verbose):
    """
    This event checks if a group discovers agriculture.

    If the event occurs a fact is added to the group.

    :param group: The group to check.
    :param world: The world.
    :param information: A dictionary with the information for the events.
    :param verbose: True if the event has to register into facts, False otherwise
    """
    if random.random() < chance_to_discover_agriculture(group, world):
        group.activities.append("Agriculture")
        fact = "{} has discovered agriculture.".format(group.name)
        if verbose:
            if information["turn"] in group.facts:
                group.facts[information["turn"]].append(fact)
            else:
                group.facts[information["turn"]] = [fact]
        if information["turn"] in group.file_facts:
            group.file_facts[information["turn"]]['agricult'] = True
        else:
            group.file_facts[information["turn"]] = {'agricult': True}


def become_sedentary(group, world, information, verbose):
    """
    This event checks if a group can evolve to sedentary.

    If the event occurs a fact is added to the group.

    :param group: The group to check.
    :param world: The world.
    :param information: A dictionary with the information for the events.
    :param verbose: True if the event has to register into facts, False otherwise
    """
    if random.random() < chance_to_become_sedentary(group):
        group.nomadism = "sedentary"
        fact = "{} is converting to sedentarism.".format(group.name)
        if verbose:
            if information["turn"] in group.facts:
                group.facts[information["turn"]].append(fact)
            else:
                group.facts[information["turn"]] = [fact]
        if information["turn"] in group.file_facts:
            group.file_facts[information["turn"]]['nomadism'] = 'sedentary'
        else:
            group.file_facts[information["turn"]] = {'nomadism': 'sedentary'}


def migrate(group, world, information, verbose):
    """
    This event checks if a group migrates from it's current position.

    If the event occurs a fact is added to the group.

    :param group: The group to check.
    :param world: The world.
    :param information: A dictionary with the information for the events.
    :param verbose: True if the event has to register into facts, False otherwise
    """
    if random.random() < chance_to_migrate(group, world, information["occupied_positions"]):
        positions = land_cells_around(world, group.position, group.migration_radius, information["occupied_positions"])
        prosperity = ([Utils.perturbate_low(group.get_prosperity(world, p)), p] for p in positions)
        best = max(prosperity)
        group.position = best[1]
        fact = "{} is moving to better lands {}.".format(group.name, best[1])
        if verbose:
            if information["turn"] in group.facts:
                group.facts[information["turn"]].append(fact)
            else:
                group.facts[information["turn"]] = [fact]

        if information["turn"] in group.file_facts:
            group.file_facts[information["turn"]]['pos'] = best[1]
        else:
            group.file_facts[information["turn"]] = {'pos': best[1]}


def dead(group, world, information, verbose):
    """
    This event checks if a group is dead.

    If the event occurs a fact is added to the group.

    :param group: The group to check.
    :param world: The world.
    :param information: A dictionary with the information for the events.
    :param verbose: True if the event has to register into facts, False otherwise
    """
    if group.is_dead:
        fact = "{} has dead.".format(group.name)
        if verbose:
            if information["turn"] in group.facts:
                group.facts[information["turn"]].append(fact)
            else:
                group.facts[information["turn"]] = [fact]
        if information["turn"] in group.file_facts:
            group.file_facts[information["turn"]]['dead'] = True
        else:
            group.file_facts[information["turn"]] = {'dead': True}


def develop_trade(group, world, information, verbose):
    """
    This event checks if a group can develop trade.

    To develop trade a group must be sedentary and have any neighbour near to commerce with them.
    :param group: The group to check.
    :param world: The world.
    :param information: A dictionary with the information for the events.
    :param verbose: True if the event has to register into facts, False otherwise
    """
    if random.random() < chance_to_develop_trade(group, information["occupied_positions"]):
        group.knows_trade = True
        fact = "{} has develop trade.".format(group.name)
        if verbose:
            if information["turn"] in group.facts:
                group.facts[information["turn"]].append(fact)
            else:
                group.facts[information["turn"]] = [fact]


def trade(group, world, information, verbose):
    """
    This event makes a trade.

    If we trade with a neighbour we update the wealth of the two groups.
    :param group: The group to check.
    :param world: The world
    :param information: A dictionary with the information for the events.
    :param verbose: True if the event has to register into facts, False otherwise
    """
    trade_chance = chance_to_trade(group, information)
    if random.random() < trade_chance[0]:
        fact = "{} is trading with: ".format(group.name)
        for n in trade_chance[1]:
            n.trade(group.prosperity)
            group.trade(n.prosperity)
            fact += n.name + " "
        if verbose:
            if information["turn"] in group.facts:
                group.facts[information["turn"]].append(fact)
            else:
                group.facts[information["turn"]] = [fact]

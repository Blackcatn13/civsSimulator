import random
import copy
from civsSimulator import Utils, Events
from civsSimulator.Tribes import *


class Group:
    """This class represents a group.

    The group will evolve using the :func:`turn`.

    :param position: The position to set the group.
    :param tribe: A dictionary containing all the custom parameters for the group.
    :param default: A dictionary containing all the default parameters for all the groups.

    The tribe parameters will be merged with the default ones.

    The current available parameters are:
        * **Biomes-prosperity-per-activity**: this entry holds the prosperity factor of every biome that defines the
          WorldEngine. This values are replicated for each activity defined in the simulation.
        * **Unhospital-biomes**: this are the biomes that will be skipped when searching for a valid position in the
          map to place the tribe.
        * **Max-initial-population**: this are the maximum values that a new created tribe can have of every type of
          person.
        * **Start-activities**: this are the starting activities that every tribe will have.
        * **Max-population-for-activity**: this defines the maximum population a tribe can have with his developed
          activities.
        * **Crowding-for-activity**: this defines how more people can the tribe support with the current activity.
        * **Mortality-rates**: this defines the different mortality rates for the different types of person.
        * **Grown-rates**: this defines the values to grown the people, the **men-women** is the relation of a child
          growing men or women (1.0 all men, 0.0 all women), the **old-men** and **old-women** are the probability of
          a young to grown old.
        * **Events**: this is a list of all the events a tribe will check every turn. The values are the function names
          of the events in the Events module. They are executed with the **group** and **world** as parameters.
        * **Migration-radius**: this is the radius a tribe will check for a better position if the event migrate
          triggers.
        * **Migration-rate**: this is a list with the probability of migrate depending the current tribe culture.

    """
    def __init__(self, position, tribe, default):
        """
        This will create a group in the given position, and with the given parameters.

        The tribe parameters will be merged with the default ones.

        :param position: The position to set the group.
        :param tribe: A dictionary containing all the custom parameters for the group.
        :param default: A dictionary containing all the default parameters for all the groups.
        """
        self._position = position
        mix_tribe = copy.deepcopy(tribe)
        def_tribe = copy.deepcopy(default)
        mix_tribe = Utils.update(mix_tribe, def_tribe)
        self._tribe = mix_tribe
        self._name = eval(mix_tribe["Name"])(mix_tribe["Name-rules"])
        self._children = random.randrange(0, mix_tribe["Max-initial-population"]["children"])
        self._young_men = random.randrange(0, mix_tribe["Max-initial-population"]["young-men"])
        self._young_women = random.randrange(0, mix_tribe["Max-initial-population"]["young-women"])
        self._old_men = random.randrange(0, mix_tribe["Max-initial-population"]["old-men"])
        self._old_women = random.randrange(0, mix_tribe["Max-initial-population"]["old-women"])
        self.activities = mix_tribe["Start-activities"]
        self._max_populations = mix_tribe["Max-population-for-activity"]
        self._biomes_prosperity_per_activity = mix_tribe["Biomes-prosperity-per-activity"]
        self._crowding_per_activity = mix_tribe["Crowding-for-activity"]
        self._mortality = mix_tribe["Mortality-rates"]
        self._grown_rates = mix_tribe["Grown-rates"]
        self._last_prosperity = 0
        self.nomadism = "nomadic"
        self._events = mix_tribe["Events"]
        self._migration_radius = mix_tribe["Migration-radius"]
        self._migration_rate = mix_tribe["Migration-rate"]
        self.facts = []

    def print_population_info(self):
        """
        Prints the population information of the group.
        """
        print("Total Population: " + str(self.total_persons) + "\n\tChildren: " + str(self._children) +
              "\n\tYoung men: " + str(self._young_men) + "\n\tYoung women: " + str(self._young_women) +
              "\n\tOld men: " + str(self._old_men) + "\n\tOld women: " + str(self._old_women) +
              "\nThe group has a " + self.nomadism + " culture" + "\nThe group lives in: %s" % (self.position,))

    @property
    def is_dead(self):
        """
        The group status.
        """
        return self.total_persons == 0

    @property
    def prosperity(self):
        """
        The last calculate prosperity for the group.
        """
        return self._last_prosperity

    @property
    def position(self):
        """
        The current position of the group.
        """
        return self._position.x, self._position.y

    @position.setter
    def position(self, value):
        """
        Sets a new position value.
        """
        self._position = Utils.Position._make(value)

    @property
    def migration_radius(self):
        """
        The current migration radius taking into account the current culture.
        """
        return self._migration_radius[self.nomadism]

    @property
    def migration_rate(self):
        """
        The current migration rate taking into account the current culture.
        """
        return self._migration_rate[self.nomadism]

    @property
    def active_persons(self):
        """
        The current active persons of the group.
        """
        return self._young_men + self._young_women

    @property
    def total_persons(self):
        """
        The current total population of the group.
        """
        return self._old_men + self._old_women + self._young_men + self._young_women + self._children

    def turn(self, world, information):
        """
        This function simulates a turn of the group.

        A turn consist of updating the population, and checking the events.

        :param world: The world in which the group lives.
        :param information: A dictionary with the information to give to the events.
        """
        if not self.is_dead:
            self._update_population(world)
            self._check_events(world, information)

    def _check_events(self, world, information):
        """
        This function calls all the events that the group has.

        :param world: The world in which the group lives.
        :param information: A dictionary with the information to give to the events.
        """
        for event in self._events:
            eval(event)(self, world, information)

    def _update_population(self, world):
        """
        This functions updates the population of the group.
        :param world: The world in which the group lives.
        """
        p = self.get_prosperity(world, self.position)
        self._last_prosperity = p
        children_delta = self._update_children(p)
        young_delta = self._update_young(p)
        old_delta = self._update_old(p)
        births_delta = self._update_births(p)
        tot_delta = list(map((lambda a, b, c, d: a + b + c + d), children_delta, young_delta, old_delta, births_delta))
        self._children += tot_delta[0]
        self._young_men += tot_delta[1]
        self._young_women += tot_delta[2]
        self._old_men += tot_delta[3]
        self._old_women += tot_delta[4]

    def get_prosperity(self, world, position):
        """
        This function returns the prosperity of the group in the given position.

        It returns the best value given all the current activities of the group.

        :param world: The world in which the group lives.
        :param position: The position to check.
        :return: The prosperity value in the given position.
        """
        return max(self.get_prosperity_per_activity(world, position))

    def get_prosperity_per_activity(self, world, position):
        """
        This function returns the prosperity of each activity of group in the given position.
        :param world: The world in which the group lives.
        :param position: The position to check.
        :return: A list with the prosperity for each activity of the group.
        """
        prosperity = []
        for activity in self.activities:
            base = self.get_base_prosperity_per_activity(activity, world, position)
            crowding = self._get_crowding_per_activity(activity)
            prosperity.append(Utils.saturate(base * crowding, 1.0))
        return prosperity

    def get_base_prosperity_per_activity(self, activity, world, position):
        """
        This functions returns the prosperity of an activity given a position.
        :param activity: The activity to get the prosperity.
        :param world: The world in which the group lives.
        :param position: The position to check.
        :return: The prosperity in that position with the given activity.
        """
        return self._biomes_prosperity_per_activity[activity][world.biome_at(position).name()]

    def _get_crowding_per_activity(self, activity):
        actives = self.active_persons
        total = self.total_persons
        max_support = self._max_populations[activity]
        pop_support = actives * self._crowding_per_activity[activity]
        pop_support = min(max_support, pop_support)
        if total < pop_support:
            return 1.0
        else:
            if pop_support == 0.0 or total == 0:
                return 0.0
            else:
                return 1.0 / (total / pop_support)

    def _update_children(self, prosp):
        mortality = self._mortality["children"] * Utils.opposite(prosp)
        n_children = self._children
        [dead, grown] = Utils.rsplit(n_children, mortality)
        [men, women] = Utils.rsplit(grown, self._grown_rates["men-women"])
        # print("Dead children: " + str(dead))
        return [-dead, men, women, 0, 0]

    def _update_young(self, prosp):
        mortality_men = self._mortality["young-men"] * Utils.opposite(prosp)
        mortality_women = self._mortality["young-women"] * Utils.opposite(prosp)
        n_young_men = self._young_men
        n_young_women = self._young_women
        [m_dead, m_alive] = Utils.rsplit(n_young_men, mortality_men)
        [w_dead, w_alive] = Utils.rsplit(n_young_women, mortality_women)
        [m_grown, m_rest] = Utils.rsplit(m_alive, self._grown_rates["old-men"])
        [w_grown, w_rest] = Utils.rsplit(w_alive, self._grown_rates["old-women"])
        # print("Dead young men: " + str(m_dead) + " dead young women: " + str(w_dead))
        return [0, -1 * (m_dead + m_grown), -1 * (w_dead + w_grown), m_grown, w_grown]

    def _update_old(self, prosp):
        mortality_men = Utils.saturate(self._mortality["old-men"] * Utils.opposite(prosp), 1.0)
        mortality_women = Utils.saturate(self._mortality["old-women"] * Utils.opposite(prosp), 1.0)
        n_old_men = self._old_men
        n_old_women = self._old_women
        [m_dead, m_alive] = Utils.rsplit(n_old_men, mortality_men)
        [w_dead, w_alive] = Utils.rsplit(n_old_women, mortality_women)
        # print("Dead old men: " + str(m_dead) + " dead old women: " + str(w_dead))
        return [0, 0, 0, -m_dead, -w_dead]

    def _update_births(self, prosp):
        n_young_men = self._young_men
        n_young_women = self._young_women
        men_availability_factor = self._get_men_availability_factor(n_young_men, n_young_women)
        women_fertility = n_young_women * self._grown_rates["women-fertility"] * Utils.perturbate_high(prosp)
        births = round(women_fertility * men_availability_factor)
        return [births, 0, 0, 0, 0]

    @staticmethod
    def _get_men_availability_factor(young_men, young_women):
        if young_women > 0:
            men_factor = young_men / young_women
            res = (men_factor * 0.5) / 2
            return Utils.saturate(Utils.saturate(res, 1.0), men_factor * 3)
        else:
            return 0

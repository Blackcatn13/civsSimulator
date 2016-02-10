import random
from civsSimulator import Utils, Events


class Group:
    def __init__(self, position, tribe, default):
        self._position = position
        mix_tribe = tribe.copy()
        mix_tribe = Utils.update(mix_tribe, default)
        self._tribe = mix_tribe
        self._name = mix_tribe["Name"]
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
        print("Total Population: " + str(self.total_persons) + "\n\tChildren: " + str(self._children) +
              "\n\tYoung men: " + str(self._young_men) + "\n\tYoung women: " + str(self._young_women) +
              "\n\tOld men: " + str(self._old_men) + "\n\tOld women: " + str(self._old_women) +
              "\nThe group has a " + self.nomadism + " culture" + "\nThe group lives in: %s" % (self.position,))

    @property
    def is_dead(self):
        return self.total_persons == 0

    @property
    def prosperity(self):
        return self._last_prosperity

    @property
    def position(self):
        return self._position.x, self._position.y

    @position.setter
    def position(self, value):
        self._position = Utils.Position._make(value)

    @property
    def migration_radius(self):
        return self._migration_radius[self.nomadism]

    @property
    def migration_rate(self):
        return self._migration_rate[self.nomadism]

    @property
    def active_persons(self):
        return self._young_men + self._young_women

    @property
    def total_persons(self):
        return self._old_men + self._old_women + self._young_men + self._young_women + self._children

    def turn(self, world, occupied_positions):
        if not self.is_dead:
            self._update_population(world)
            self._check_events(world, occupied_positions)

    def _check_events(self, world, occupied_positions):
        for event in self._events:
            eval(event)(self, world, occupied_positions)

    def _update_population(self, world):
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
        return max(self.get_prosperity_per_activity(world, position))

    def get_prosperity_per_activity(self, world, position):
        prosperity = []
        for activity in self.activities:
            base = self.get_base_prosperity_per_activity(activity, world, position)
            crowding = self._get_crowding_per_activity(activity)
            prosperity.append(Utils.saturate(base * crowding, 1.0))
        return prosperity

    def get_base_prosperity_per_activity(self, activity, world, position):
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

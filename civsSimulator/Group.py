import random
from civsSimulator import Utils


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
        self._activities = mix_tribe["Start-activities"]
        self._max_populations = mix_tribe["Max-population-for-activity"]
        self._biomes_prosperity_per_activity = mix_tribe["Biomes-prosperity-per-activity"]
        self._crowding_per_activity = mix_tribe["Crowding-for-activity"]
        self._mortality = mix_tribe["Mortality-rates"]
        self._grown_rates = mix_tribe["Grown-rates"]
        self.print_population_info()

    def print_population_info(self):
        print("Children: " + str(self._children) + " Young men: " + str(self._young_men) + " Young women: " + str(
            self._young_women) + " old men: " + str(self._old_men) + " old women: " + str(self._old_women))

    def turn(self, world):
        self._update_population(world)

    def _update_population(self, world):
        p = self._get_prosperity(world)
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

    def _get_prosperity(self, world):
        return max(self._get_prosperity_per_activity(world))

    def _get_prosperity_per_activity(self, world):
        prosperity = []
        for activity in self._activities:
            base = self._get_base_prosperity_per_activity(activity, world)
            crowding = self._get_crowding_per_activity(activity)
            prosperity.append(Utils.saturate(base * crowding, 1.0))
        return prosperity

    def _get_base_prosperity_per_activity(self, activity, world):
        return self._biomes_prosperity_per_activity[activity][world.biome_at((self._position.x,
                                                                              self._position.y)).name()]

    def _get_crowding_per_activity(self, activity):
        actives = self.get_active_persons()
        total = self.get_total_persons()
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

    def get_active_persons(self):
        return self._young_men + self._young_women

    def get_total_persons(self):
        return self._old_men + self._old_women + self._young_men + self._young_women + self._children

    def _update_children(self, prosp):
        mortality = self._mortality["children"] * Utils.opposite(prosp)
        n_children = self._children
        [dead, grown] = Utils.rsplit(n_children, mortality)
        [men, women] = Utils.rsplit(grown, self._grown_rates["men-women"])
        print("Dead children: " + str(dead))
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
        print("Dead young men: " + str(m_dead) + " dead young women: " + str(w_dead))
        return [0, -1 * (m_dead + m_grown), -1 * (w_dead + w_grown), m_grown, w_grown]

    def _update_old(self, prosp):
        mortality_men = Utils.saturate(self._mortality["old-men"] * Utils.opposite(prosp), 1.0)
        mortality_women = Utils.saturate(self._mortality["old-women"] * Utils.opposite(prosp), 1.0)
        n_old_men = self._old_men
        n_old_women = self._old_women
        [m_dead, m_alive] = Utils.rsplit(n_old_men, mortality_men)
        [w_dead, w_alive] = Utils.rsplit(n_old_women, mortality_women)
        print("Dead old men: " + str(m_dead) + " dead old women: " + str(w_dead))
        return [0, 0, 0, -m_dead, -w_dead]

    def _update_births(self, prosp):
        n_young_men = self._young_men
        n_young_women = self._young_women
        men_availability_factor = self._get_men_availability_factor(n_young_men, n_young_women)
        women_fertility = n_young_women * self._grown_rates["women-fertility"] * Utils.perturbate_high(prosp)
        births = round(women_fertility * men_availability_factor)
        return [births, 0, 0, 0, 0]

    def _get_men_availability_factor(self, young_men, young_women):
        if young_women > 0:
            men_factor = young_men / young_women
            res = (men_factor * 0.5) / 2
            return Utils.saturate(Utils.saturate(res, 1.0), men_factor * 3)
        else:
            return 0

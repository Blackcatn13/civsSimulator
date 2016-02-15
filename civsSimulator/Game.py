import json
import random
from worldengine.world import World
from civsSimulator.Group import Group
from civsSimulator import Utils, GlobalEvents


class Game:

    def __init__(self, config, world):
        self.groups = []
        self._config = {}
        self.load_config(config)
        self._world = World.open_protobuf(world)
        self._turn = 0
        self._global_events = self._config["Tribe"]["General"]["Global-events"]

    def load_config(self, config):
        with open(config) as data_file:
            self._config = json.load(data_file)

    def create_group(self):
        tribe_info = random.choice(self._config["Tribe"]["Tribes"])
        if "Unhospital-biomes" in tribe_info:
            unhosp_biomes = tribe_info["Unhospital-biomes"]
        else:
            unhosp_biomes = self._config["Tribe"]["General"]["Unhospital-biomes"]

        p = Utils.Position(random.randrange(0, self._world.width), random.randrange(0, self._world.height))
        while self._world.biome_at((p.x, p.y)).name() in unhosp_biomes:
            p = Utils.Position(random.randrange(0, self._world.width), random.randrange(0, self._world.height))
        t = Group(p, tribe_info, self._config["Tribe"]["General"])
        self.groups.append(t)

    def turn(self):
        self._turn += 1
        occupied_positions = [g.position for g in self.groups]
        tribes_type = [g.type for g in self.groups]
        information = {"occupied_positions": occupied_positions, "turn": self._turn, "tribes-type": tribes_type,
                       "groups": self.groups}
        for group in self.groups:
            group.turn(self._world, information)
        for e in self._global_events:
            eval(e[0])(self._world, information, e[1])

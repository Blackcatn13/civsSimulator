import json
import random
from worldengine.world import World
from collections import namedtuple
from civsSimulator.Group import Group

Position = namedtuple('Position', ['x', 'y'])


class Game:

    def __init__(self, config, world):
        self._groups = []
        self._config = {}
        self.load_config(config)
        self._world = World.open_protobuf(world)

    def load_config(self, config):
        with open(config) as data_file:
            self._config = json.load(data_file)

    def create_group(self):
        tribe_info = random.choice(self._config["Tribe"]["Tribes"])
        if "Unhospital-biomes" in tribe_info:
            unhosp_biomes = tribe_info["Unhospital-biomes"]
        else:
            unhosp_biomes = self._config["Tribe"]["General"]["Unhospital-biomes"]

        p = Position(random.randrange(0, self._world.width), random.randrange(0, self._world.height))
        while self._world.biome_at((p.x, p.y)).name() in unhosp_biomes:
            p = Position(random.randrange(0, self._world.width), random.randrange(0, self._world.height))
        t = Group(p, tribe_info, self._config["Tribe"]["General"])
        self._groups.append(t)

    def turn(self):
        for group in self._groups:
            group.turn(self._world)

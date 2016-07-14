from civsSimulator.Game import Game
import argparse
import json


def main():

    parser = argparse.ArgumentParser(prog="civsSimulator")
    parser.add_argument('world', help='.world file where the groups will be simulated.')
    parser.add_argument('config', help='.json with the configuration of the tribes.')
    parser.add_argument('--groups', help='The number of groups that will be created to simulate.', default=20, type=int)
    parser.add_argument('--turn', help='The number of turns the simulation will run.', default=50, type=int)
    parser.add_argument('--verbose', '-v', help='Prints the facts that happen.', nargs='?', default=False,
                        const=True, type=bool)
    parser.add_argument('-o', '--output', help='File to save the facts.', default="facts.txt")
    opt = parser.parse_args()
    g = Game(opt.config, opt.world)
    for i in range(opt.groups + 1):
        g.create_group()

    for i in range(opt.turn + 1):
        g.turn()
        facts = []
        for x in g.groups:
            if i in x.facts:
                facts.extend(x.facts[i])
        if opt.verbose:
            if facts:
                print("========================================")
                print("=========      In turn {}      =========".format(i))
                print("========================================")
                for x in facts:
                    print(x)
    dead = 0
    for x in g.groups:
        if x.is_dead:
            dead += 1
    print("\nAt the end {} groups have perished in history".format(dead))
    f = open(opt.output, 'w')
    saveFacts = [{} for i in range(opt.turn + 1)]
    for i in range(opt.turn + 1):
        facts = []
        for x in g.groups:
            if i in x.file_facts:
                facts.extend([{'id': x.id, 'name': x.name, 'fact': x.file_facts[i]}])
        if facts:
            saveFacts[i] = facts
    json.dump(saveFacts, f)
    f.close()

if __name__ == "__main__":
    main()

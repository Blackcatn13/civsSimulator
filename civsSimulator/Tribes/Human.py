from civsSimulator.Generator import NameGenerator
import random


def get_name(name_rules):
    try:
        n = NameGenerator(name_rules["vowels"], name_rules["consonants"], name_rules["syllables"])
        return n.compose(random.randint(1, name_rules["max-syllables"]))
    except AssertionError as err:
        return "Human-non-generated-name"

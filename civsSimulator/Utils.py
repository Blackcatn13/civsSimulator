import random
import collections
from collections import namedtuple


Position = namedtuple('Position', ['x', 'y'])


def saturate(value, sat_max):
    return sat_max if value > sat_max else (value if value > 0.0 else 0.0)


def opposite(value):
    return 1.0 - value


def rsplit(times, factor):
    ret = [0, 0]
    for n in range(int(times)):
        if random.random() < factor:
            ret[0] += 1
        else:
            ret[1] += 1
    return ret


def update(d, u):
    for k, v in u.items():
        if isinstance(v, collections.Mapping):
            r = update(d.get(k, {}), v)
            d[k] = r
        else:
            if k in d:
                pass
            else:
                d[k] = u[k]
    return d


def perturbate(n, pert_factor):
    perturbation = (random.random() - 0.5) * pert_factor
    return saturate(n + perturbation, 1.0)


def perturbate_high(n):
    return perturbate(n, 1.0)


def perturbate_med(n):
    return perturbate(n, 0.33)


def perturbate_low(n):
    return perturbate(n, 0.2)


def add_list(l1, l2):
    return tuple([i1 + i2 for i1, i2 in zip(l1, l2)])

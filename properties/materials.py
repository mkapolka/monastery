import properties as p
from material import Material


class Metal(Material):
    name = 'metal'
    properties = [p.Hard]


class Stone(Material):
    name = 'stone'
    properties = [p.Hard]


class Wood(Material):
    name = 'wood'
    properties = [p.Flammable, p.Phlogiston]


class Flesh(Material):
    name = 'flesh'
    properties = [p.Flammable, p.Phlogiston]


class Plant(Material):
    name = 'plant matter'
    properties = [p.Flammable, p.Phlogiston]

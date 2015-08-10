import properties as p
from material import Material


class Metal(Material):
    name = 'metal'
    properties = [p.Hard]
    hp = 10


class Stone(Material):
    name = 'stone'
    properties = [p.Hard]
    hp = 8


class Wood(Material):
    name = 'wood'
    properties = [p.Flammable, p.Phlogiston]
    hp = 5


class Flesh(Material):
    name = 'flesh'
    properties = [p.Flammable, p.Phlogiston, p.Soft, p.Digestible]
    hp = 3


class Plant(Material):
    name = 'plant matter'
    properties = [p.Flammable, p.Phlogiston]
    hp = 2

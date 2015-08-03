from properties import Hard, Flammable, Phlogiston
from material import Material


class Metal(Material):
    name = 'metal'
    properties = [Hard]


class Stone(Material):
    name = 'stone'
    properties = [Hard]


class Wood(Material):
    name = 'wood'
    properties = [Flammable, Phlogiston]


class Flesh(Material):
    properties = [Flammable, Phlogiston]

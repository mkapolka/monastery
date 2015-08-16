import properties as p
from material import Material


class Flesh(Material):
    name = 'flesh'
    properties = [p.Flammable, p.Phlogiston, p.Soft, p.Decomposable]
    hp = 3
    damage_mod = 1


class Leather(Material):
    name = 'leather'
    properties = [p.Soft, p.Flammable, p.Phlogiston]
    hp = 4
    damage_mod = 1


class Metal(Material):
    name = 'metal'
    properties = [p.Hard]
    hp = 10
    damage_mod = 2


class Plant(Material):
    name = 'plant matter'
    properties = [p.Flammable, p.Phlogiston]
    hp = 2
    damage_mod = .1


class Stone(Material):
    name = 'stone'
    properties = [p.Hard]
    hp = 8
    damage_mod = 1


class Wood(Material):
    name = 'wood'
    properties = [p.Flammable, p.Phlogiston]
    hp = 5
    damage_mod = .5

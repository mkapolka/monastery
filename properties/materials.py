from properties import *
from material import Material

class Metal(Material):
    properties = [Hard]

class Wood(Material):
    properties = [Flammable, Phlogiston]

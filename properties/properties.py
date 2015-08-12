from property import Property


class Absorbant(Property):
    types = ['mechanical', 'physical']
    description = 'is absorbant'


class Bladed(Property):
    types = ["mechanical"]
    description = 'is bladed'


class Boiling(Property):
    types = []
    description = 'is boiling'


class Boilable(Property):
    types = ["physical"]
    description = 'can be boiled'


class Burning(Property):
    types = []
    description = 'is burning'


class Decomposable(Property):
    types = ['physical']
    description = 'will rot'


class Dissolvable(Property):
    types = ['physical', 'mechanical']
    description = 'can be dissolved into water'


class Digestible(Property):
    types = ['physical']
    description = 'can be digested'


class Edible(Property):
    types = ['physical']
    description = 'is edible'


class Flammable(Property):
    types = ['physical']
    description = 'is flammable'


class Hard(Property):
    types = ['physical']
    description = 'is hard'


class Heavy(Property):
    types = ['physical']
    description = 'is heavy'


class HealsWounds(Property):
    types = ['chemical']
    description = 'heals wounds'


class Hot(Property):
    types = []
    description = 'is hot'


class Immobile(Property):
    types = []
    description = 'cannot be moved'


class Liquid(Property):
    types = ['mechanical']
    description = 'is liquid'


class MortarShaped(Property):
    types = ['mechanical']


class Open(Property):
    types = ['mechanical']
    description = 'is open'


class Openable(Property):
    types = ['mechanical']
    description = 'can be opened'


class Phlogiston(Property):
    types = ['physical']
    description = 'will be consumed by fire'


class Sews(Property):
    types = ['mechanical']
    description = 'can be used to sew things'


class Soft(Property):
    types = ['physical']
    description = 'is soft'


class ShrinkOnEat(Property):
    types = ['chemical']
    description = 'will shrink the ingester'


class SpringsWater(Property):
    types = []
    description = 'produces water'


class TeapotShaped(Property):
    types = ['mechanical']

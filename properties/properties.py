from property import Property


class Absorbant(Property):
    types = ['mechanical', 'physical']
    description = 'is absorbant'


class Antidote(Property):
    types = ['chemical']
    description = 'cures poison'


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


class Breathes(Property):
    types = ['mechanical']
    description = 'breathes'


class Decomposable(Property):
    types = ['physical']
    description = 'will rot'


class Dissolvable(Property):
    types = ['physical', 'mechanical']
    description = 'can be dissolved into water'


class Edible(Property):
    types = ['chemical']
    description = 'is edible'


class Flammable(Property):
    types = ['physical']
    description = 'is flammable'


class Gas(Property):
    types = ['mechanical']
    description = 'is gaseous'


class Hard(Property):
    types = ['physical']
    description = 'is hard'


class Heavy(Property):
    types = ['physical']
    description = 'is heavy'


class HealsWounds(Property):
    types = ['chemical']
    description = 'heals wounds'


class HeatsContents(Property):
    types = ['mechanical']
    description = 'heats its contents'


class Hot(Property):
    types = []
    description = 'is hot'


class Immobile(Property):
    types = ['mechanical']
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


class Pinchable(Property):
    types = ['mechanical']
    description = 'has leaves that can be pinched off'


class Phlogiston(Property):
    types = ['physical']
    description = 'will be consumed by fire'


class PoisonImmune(Property):
    types = ['physical']
    description = 'is immune to poison'


class Poisonous(Property):
    types = ['chemical']
    description = 'is poisonous'


class Poisoned(Property):
    types = ['mechanical', 'physical', 'wound']
    description = 'is poisoned'


class Sews(Property):
    types = ['mechanical']
    description = 'can be used to sew things'


class Slatherable(Property):
    types = ['mechanical']
    description = 'can be slathered onto things'


class Soft(Property):
    types = ['physical']
    description = 'is soft'


class ShrinkOnEat(Property):
    types = ['chemical']
    description = 'will shrink the ingester'


class Thickens(Property):
    types = ['chemical']
    description = 'acts as a thickening agent'


class TeapotShaped(Property):
    types = ['mechanical']

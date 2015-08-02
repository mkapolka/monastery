from property import Property

class Burning(Property):
    types = []
    description = 'is burning'

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

class Holdable(Property):
    types = ['mechanical']
    description = 'can be picked up'

class Hot(Property):
    types = []
    description = 'is hot'

class Immobile(Property):
    types = []
    description = 'cannot be moved'

class Open(Property):
    types = ['mechanical']
    description = 'is open'

class Openable(Property):
    types = ['mechanical']
    description = 'can be opened'

class Phlogiston(Property):
    types = ['physical']
    description = 'will be consumed by fire'

class ShrinkOnEat(Property):
    types = ['chemical']
    description = 'will shrink the ingester'

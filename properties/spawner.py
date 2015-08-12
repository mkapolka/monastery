from property import Property
import templates as t

class Spawner(Property):
    types = []
    description = 'will spawn things'
    template = None

    def __init__(self, *args, **kwargs):
        super(Spawner, self).__init__(*args, **kwargs)
        self._spawned = []

    @property
    def spawned_things(self):
        self._check_and_removed_destroyed()
        return self._spawned

    def add_thing(self, thing):
        self._spawned.append(thing)

    def _check_and_removed_destroyed(self):
        self._spawned = [s for s in self._spawned if not s.destroyed]


class SpawnsMice(Spawner):
    types = ['mechanical']
    description = 'spawns mice'
    template = t.Mouse
    max_things = 1

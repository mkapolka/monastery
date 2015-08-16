from property import Property
import templates as t


class Spawner(Property):
    types = []
    description = 'will spawn things'
    template = None

    @classmethod
    def key(self):
        return 'Spawner'

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

    spawn_message = '%(thing)s crawls out of %(me)s'


class SpawnsFrogs(Spawner):
    types = ['mechanical']
    description = 'little tadpoles are swimming around in it'
    template = t.Frog
    max_things = 2

    spawn_message = 'a tadpole grows up into a frog.'


class SpawnsRabbits(Spawner):
    types = ['mechanical']
    description = 'spawns rabbits'
    template = t.Rabbit
    max_things = 1

    spawn_message = '%(thing)s crawls out of %(me)s'

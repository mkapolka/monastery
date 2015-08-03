import itertools

from location import Location, StaticExit
from templates.templates import Firepit, Teapot, Barrel, Mortar

places = {
    "monastery_garden": {
        "name": "The Monastery Garden",
        "exits": ["monastery_kitchen"],
        "things": []
    },
    "monastery_kitchen": {
        "name": "Brother Buddy's Kitchen",
        "exits": ["monastery_garden"],
        "things": [Firepit, Teapot, Barrel, Mortar]
    }
}


def make_locations(places):
    output = {}
    for key, value in places.items():
        output[key] = Location()
        output[key].name = value['name']
        for thing_class in value.get('things', []):
            output[key].add_thing(thing_class.instantiate())

    for key, value in places.items():
        for exit_id in value['exits']:
            output[key].exits.append(StaticExit(output[key], output[exit_id]))

    return output


def _recurse_thing_locations(thing):
    return itertools.chain(*[
        _recurse_location(l) for l in thing.locations
    ])


def _recurse_location(location):
    return itertools.chain([location], *[
        _recurse_thing_locations(t) for t in location.things
    ])


class World(object):
    def __init__(self):
        self.locations = make_locations(places)

    def get_all_locations(self):
        return itertools.chain(*[
            _recurse_location(l) for l in self.locations.values()
        ])

    def get_all_things(self):
        return itertools.chain(*[
            l.things for l in self.get_all_locations()
        ])

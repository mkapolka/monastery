import itertools

from location import Location, StaticExit
from templates.templates import Oven, Barrel, Mortar, Cat, instantiate_template
import templates as t
import templates.spawner_templates as st
from utils import flatten_array

places = {
    "monastery_garden": {
        "name": "The Monastery Garden",
        "exits": ["monastery_kitchen", "outside_monastery"],
        "things": [Cat, t.Well, st.MouseHole]
    },
    "monastery_kitchen": {
        "name": "Brother Buddy's Kitchen",
        "exits": ["monastery_garden", "monastery_solar", "monastery_closet"],
        "things": [Oven, t.TeaKettle, Barrel, t.Knife]
    },
    "monastery_solar": {
        "name": "the solar",
        "exits": ["monastery_kitchen"],
        "things": [t.ShrinkyMushroom, Mortar, t.NeedleAndThread]
    },
    "monastery_closet": {
        "name": "the broom closet",
        "exits": ["monastery_kitchen"],
        "things": [t.ShrinkyMushroom, t.Bucket, t.Sponge, t.Mouse]
    },
    "outside_monastery": {
        "name": "along the bright trail",
        "exits": ["monastery_garden", "creekbed"],
        "things": []
    },
    "creekbed": {
        "name": "a dry creekbed",
        "exits": ["outside_monastery", "thicket"],
        "things": [t.WillowRoot]
    },
    "thicket": {
        "name": "a thorny thicket",
        "exits": ["creekbed", "wolf_den"],
        "things": [t.WillowRoot]
    },
    "wolf_den": {
        "name": "the wolves' den",
        "exits": ["thicket"],
        "things": [t.CustomTemplate(t.Wolf, name='a white wolf'),
                   t.CustomTemplate(t.Wolf, name='a grey wolf'),
                   t.CustomTemplate(t.Wolf, name='a black wolf')]
    }
}


def make_locations(places):
    output = {}
    for key, value in places.items():
        output[key] = Location()
        output[key].name = value['name']

    for key, value in places.items():
        for exit_id in value['exits']:
            output[key].exits.append(StaticExit(output[key], output[exit_id]))

    for key, value in places.items():
        for thing_class in value.get('things', []):
            thing = instantiate_template(thing_class, output[key])
            if thing.ai_context and not thing.ai_context.home:
                thing.ai_context.home = output[key]
            output[key].add_thing(thing)

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
        return flatten_array([
            _recurse_location(l) for l in self.locations.values()
        ])

    def get_all_things(self):
        return flatten_array([
            l.things for l in self.get_all_locations()
        ])

import itertools
import re

from location import Location, StaticExit
from templates.templates import Oven, Barrel, Mortar, Cat, instantiate_template
import templates as t
import templates.spawner_templates as st
import properties.spawner as sp
import properties as p
from utils import flatten_array

places = {
    "monastery_garden": {
        "name": "The Monastery Garden",
        "exits": ["monastery_kitchen", "monastery_guest_house", "forest_outside_monastery"],
        "things": [Cat, st.Well, st.MouseHole, t.WineSkin]
    },
    "monastery_kitchen": {
        "name": "Brother Buddy's Kitchen",
        "exits": ["monastery_garden", "monastery_closet"],
        "things": [Oven, t.TeaKettle, Barrel, t.Knife, t.Butter]
    },
    "monastery_guest_house": {
        "name": "the guest house",
        "exits": ["monastery_garden"],
        "things": [t.ShrinkyMushroom, Mortar, t.NeedleAndThread]
    },
    "monastery_closet": {
        "name": "the broom closet",
        "exits": ["monastery_kitchen"],
        "things": [t.ShrinkyMushroom, t.Bucket, t.Sponge, t.Mouse]
    },
    "forest_outside_monastery": {
        "name": "along the bright trail",
        "exits": ["monastery_garden", "forest_creekbed", "forest_trees", "forest_bridge"],
        "things": []
    },
    "forest_trees": {
        "name": "among the trees",
        "exits": ["forest_outside_monastery", "forest_clearing"],
        "things": [t.Thistle, t.CustomTemplate(t.Sapling, name='a willow sapling', properties_append=[p.HealsWounds])]
    },
    "forest_clearing": {
        "name": "in a clearing",
        "exits": ["forest_trees"],
        "things": [t.WillowRoot, st.RabbitHole, t.CustomTemplate(t.Sapling, name='a marshmallow bush', properties_append=[p.Thickens])]
    },
    "forest_creekbed": {
        "name": "a dry creekbed",
        "exits": ["forest_outside_monastery", "forest_thicket", "forest_under_bridge"],
        "things": [t.WillowRoot]
    },
    "forest_thicket": {
        "name": "a thorny thicket",
        "exits": ["forest_creekbed", "forest_wolf_den", "forest_pond"],
        "things": [t.WillowRoot, t.Thistle]
    },
    "forest_pond": {
        "name": "a smelly pool",
        "exits": ["forest_thicket"],
        "things": [t.CustomTemplate(t.Water, name='some fetid water', properties_append=[sp.SpawnsFrogs, p.Poisonous])],
    },
    "forest_wolf_den": {
        "name": "the wolves' den",
        "exits": ["forest_thicket"],
        "things": [t.CustomTemplate(t.Wolf, name='a white wolf'),
                   t.CustomTemplate(t.Wolf, name='a black wolf')]
    },
    "forest_under_bridge": {
        "name": "under the bridge",
        "exits": ["forest_creekbed", "forest_bridge"],
        "things": [t.Troll]
    },
    "forest_bridge": {
        "name": "on the bridge",
        "exits": ["forest_outside_monastery", "forest_under_bridge"]
    }
}


def make_locations(places):
    output = {}
    for key, value in places.items():
        output[key] = Location()
        output[key].name = value['name']
        zone = re.search('(\w+)_', value['name'])
        output[key].zone = zone

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
    try:
        return itertools.chain(*[
            _recurse_location(l) for l in thing.locations
        ])
    except RuntimeError:
        raise Exception(thing)


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

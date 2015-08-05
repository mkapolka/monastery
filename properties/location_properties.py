import itertools

from property import Property
from properties import Open
from location import PropertyLocation, StaticExit, OutsideExit, EntranceExit
from utils import flatten_array


def get_location_properties(thing):
    return [
        p for p in thing.properties.values() if isinstance(p, LocationProperty)
    ]


def get_all_locations(thing):
    return itertools.chain(*[
        lp.locations.values() for lp in get_location_properties(thing)
    ])


def entrances_to_thing(thing):
    output = []
    for location_property in get_location_properties(thing):
        for entrance in location_property.entrances:
            output.append(entrance)
    return output


def get_all_contents(thing):
    return itertools.chain(*[
        l.things for l in get_all_locations(thing)
    ])


def is_location_accessible(location, for_whom):
    return True


def get_accessible_locations(thing):
    things = thing.location.things
    entrances = flatten_array([entrances_to_thing(t) for t in things])
    return [thing.location] + [
        e.to_location for e in entrances if e.can_access(thing)
    ]


def get_accessible_things(thing):
    return itertools.chain(*[
        l.things for l in get_accessible_locations(thing)
    ])


class LocationProperty(Property):
    def __init__(self, thing, *args):
        super(LocationProperty, self).__init__(thing, *args)
        self.locations = {}
        self.entrances = []
        for key, loc in self.locations_template.items():
            location = PropertyLocation(self)
            location.name_template = loc['name']
            self.locations[key] = location

        for key, loc in self.locations_template.items():
            for exit in loc['exits']:
                location_key = exit['to']
                location = self.locations[key]
                requires = exit.get('requires', None)
                if location_key == 'outside':
                    exit_instance = OutsideExit(location, self.thing, requires)
                else:
                    exit_instance = StaticExit(location, self.locations[location_key])
                if 'where' in exit:
                    exit_instance.description_template = exit['where']
                location.exits.append(exit_instance)

        if hasattr(self, 'entrances_template'):
            for entrance in self.entrances_template:
                requires = entrance.get('requires', None)
                entrance_exit = EntranceExit(thing, self.locations[entrance['to']], requires)
                if 'description' in entrance:
                    entrance_exit.description_template = entrance['description']
                self.entrances.append(entrance_exit)

    def add_thing(self, thing, location_key=None):
        if not location_key:
            location = self.locations.values()[0]
        else:
            location = self.locations[location_key]
        location.add_thing(thing)

    def get_all_things(self):
        return itertools.chain(*[location.things for location in self.locations.values()])

    def destroy(self):
        names = map(lambda x: x.name, self.get_all_things())
        if len(names) > 1:
            names[-1] = "and %s" % names[-1]
        self.thing.location.tell("%s tumble%s out of %s" % (", ".join(names), '' if len(names) > 1 else 's', self.thing.name))
        for thing in self.get_all_things():
            self.thing.location.add_thing(thing)


class IsContainer(LocationProperty):
    types = ['mechanical']

    locations_template = {
        'contents': {
            'name': 'Inside %(thing_name)s',
            'exits': [
                {
                    'to': 'outside',
                    'description': 'Out to %(to_location)s',
                    'requires': [Open]
                }
            ]
        }
    }

    entrances_template = [
        {
            'to': 'contents',
            'description': 'Into %(thing)s',
            'requires': [Open]
        }
    ]


class HasStomach(LocationProperty):
    types = ['mechanical']

    locations_template = {
        'contents': {
            'name': "Inside %(thing_name)s's stomach",
            'exits': [{'to': 'outside', 'description': "Through %(thing)s's esophagus"}]
        }
    }


class Inventory(LocationProperty):
    locations_template = {
        'inventory': {
            'name': "Inside %(thing_name)s's backpack",
            'exits': [{'to': 'outside', 'description': 'Out'}]
        }
    }

    entrances_template = [
        {
            'to': 'inventory',
            'description': "Into %(thing)s's backpack"
        }
    ]

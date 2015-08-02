import itertools

from property import Property
from location import Location, PropertyLocation, StaticExit, OutsideExit, EntranceExit

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
                if location_key == 'outside':
                    exit_instance = OutsideExit(location, self.thing)
                else:
                    exit_instance = StaticExit(location, self.locations[location_key])
                if 'where' in exit:
                    exit_instance.description_template = exit['where']
                location.exits.append(exit_instance)

        if hasattr(self, 'entrances_template'):
            for entrance in self.entrances_template:
                entrance_exit = EntranceExit(thing, self.locations[entrance['to']])
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

class IsContainer(LocationProperty):
    locations_template = {
        'contents': {
            'name': 'Inside %(thing_name)s',
            'exits': [{'to': 'outside', 'description': 'Out to %(to_location)s'}]
        }
    }

    entrances_template = [
        {
            'to': 'contents',
            'description': 'Into %(thing)s'
        }
    ]

class HasStomach(LocationProperty):
    locations_template = {
        'contents': {
            'name': "Inside %(thing_name)s's stomach",
            'exits': [{'to': 'outside', 'description': "Through %(thing)s's esophagus"}]
        }
    }


class Inventory(LocationProperty):
    locations_template = {
        'inventory': {
            'name': "Inside %(thing_name)s's inventory",
            'exits': [{'to': 'outside', 'description': 'Out'}]
        }
    }

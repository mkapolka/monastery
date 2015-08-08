import itertools

from enums import Size
from property import Property
from properties import Open
from location import PropertyLocation, StaticExit, OutsideExit, EntranceExit
from utils import flatten_array


def are_touching(thing, other_thing):
    if thing.location != other_thing.location:
        return False

    if thing.location.size == Size.room:
        return False

    return True


def get_location_properties(thing):
    return [
        p for p in thing.properties.values() if isinstance(p, LocationProperty)
    ]


def get_all_locations(thing):
    return [x for x in itertools.chain(*[
        lp.locations.values() for lp in get_location_properties(thing)
    ])]


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


def _recurse_locations(location, location_filter=None, thing_filter=None, entrance_filter=None):
    tf = lambda x: True
    location_filter = location_filter or tf
    thing_filter = thing_filter or tf
    entrance_filter = entrance_filter or tf

    if location_filter(location):
        return [location] + flatten_array([
            _recurse_locations(e.to_location, location_filter, thing_filter, entrance_filter)
            for e in flatten_array([
                entrances_to_thing(t) for t in location.things if thing_filter(t)
            ]) if entrance_filter(e)
        ])
    else:
        return []


def get_accessible_locations(thing):
    return _recurse_locations(thing.location, entrance_filter=lambda e: e.can_access(thing))


def get_accessible_things(thing):
    return itertools.chain(*[
        l.things for l in get_accessible_locations(thing)
    ])


def get_visible_locations(thing):
    return _recurse_locations(thing.location, entrance_filter=lambda e: e.can_view(thing))


def get_visible_things(thing):
    return flatten_array([
        l.things for l in get_visible_locations(thing)
    ])


def add_to_contents(container, thing):
    if container.is_property(IsContainer):
        container.is_property(IsContainer).add_thing(thing)


def container_location(container):
    if container.is_property(IsContainer):
        return container.get_property(IsContainer).locations.values()[0]


def add_to_inventory(container, thing):
    if container.is_property(Inventory):
        container.get_property(Inventory).add_thing(thing)


def inventory_location(container):
    if container.is_property(Inventory):
        return container.get_property(Inventory).locations.values()[0]


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
                requires = entrance.get('requires', [])
                accessing_requires = entrance.get('accessing_requires', []) + requires
                traversing_requires = entrance.get('traversing_requires', []) + requires
                viewing_requires = entrance.get('viewing_requires', []) + requires
                entrance_exit = EntranceExit(thing, self.locations[entrance['to']], accessing_requires, viewing_requires, traversing_requires)
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
                    'requires': [Open],
                }
            ]
        }
    }

    entrances_template = [
        {
            'to': 'contents',
            'description': 'Into %(thing)s',
            'requires': [Open],
            'viewing_requires': [Open]
        }
    ]


class Surface(LocationProperty):
    types = ['mechanical']

    locations_template = {
        'top': {
            'name': 'Atop %(thing_name)s',
            'exits': [
                {
                    'to': 'outside',
                    'description': 'Off of %(thing_name)s',
                }
            ]
        }
    }

    entrances_template = [
        {
            'to': 'top',
            'description': 'Onto %(thing)s'
        }
    ]


class HasStomach(LocationProperty):
    types = ['mechanical']

    locations_template = {
        'contents': {
            'name': "Inside %(thing_name)s's stomach",
            'exits': [
                {
                    'to': 'outside',
                    'description': "Through %(thing)s's esophagus"
                }
            ],
        }
    }

    entrances_template = [
        {
            'to': 'contents',
            'description': "Into %(thing)s's stomach",
            'requires': [Open],
        }
    ]


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

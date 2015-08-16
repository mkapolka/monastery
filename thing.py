import collections
from enums import Size
from properties.location_properties import LocationProperty, get_visible_locations
import ui

message_queue = collections.deque()


def queue_message(thing, message, to_whom='self'):
    message_queue.append((thing, thing.location, message, to_whom))


def flush_message_queue(player):
    visible_locations = get_visible_locations(player)
    for thing, location, message, to_whom in message_queue:
        if to_whom == 'others':
            if location in visible_locations and thing != player:
                ui.message(message)
        elif to_whom == 'room':
            if location == player.location:
                ui.message(message)
        else:  # to_whom == 'self'
            if thing == player:
                ui.message(message)
    message_queue.clear()


def destroy_thing(thing):
    thing.destroyed = True


def cleanup_thing(thing):
    if thing.destroyed:
        for prop in thing.properties.values():
            prop.destroy()
        thing.properties = {}
        thing.form = None
        thing.material = None
        thing.location.remove_thing(thing)


def calc_hp(thing, **changes):
    size = changes.pop('size', None) or thing.size
    size_mod = pow(2, size)
    material = changes.pop('material', None) or thing.material
    material_hp = material.hp if material else 1
    return material_hp * size_mod


class Thing(object):
    def __init__(self):
        self.name = "A thing"
        self.icon = "?"
        self.properties = {}
        self.location = None
        self.form = None
        self.material = None
        self._size = Size.medium
        self.is_player = False
        self.destroyed = False
        self.ai = None
        self.ai_context = None

        self.hp = 0
        self.damage = 1
        self.damage_type = 'bludgeon'

    def __repr__(self):
        return '<Thing:%s>' % self.name

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        self._size = value
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    @property
    def hp(self):
        return self._hp

    @hp.setter
    def hp(self, value):
        self._hp = value
        if self._hp > self.max_hp:
            self._hp = self.max_hp

    @property
    def max_hp(self):
        return calc_hp(self)

    @property
    def health_percentage(self):
        return float(self.hp) / self.max_hp

    def attack(self, damage, damage_type, aggressor=None):
        was_alive = self.alive
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0
        if was_alive and not self.alive:
            self.broadcast("%s dies" % self.name)
            self.tell("You die...")

    @property
    def alive(self):
        return (self.ai is not None or self.is_player) and self.hp > self.max_hp / 2

    def tell(self, message):
        queue_message(self, message, 'self')

    def tell_room(self, message):
        queue_message(self, message, 'room')

    def broadcast(self, message):
        queue_message(self, message, 'others')

    def duplicate(self):
        """
        This handles several things incorrectly. Location properties and AIs primarily.
        TODO: Revisit
        """
        output = Thing()
        for key, value in self.__dict__.items():
            if key not in ['properties', 'ai', 'ai_context']:
                output.__dict__[key] = value
        self.location.add_thing(output)
        for key, value in self.properties.items():
            output.properties[key] = value.clone(output)
        return output

    def send_message(self, message_type, *args, **kwargs):
        for prop in self.properties.values():
            prop.receive_message(message_type, *args, **kwargs)

    def __get_property(self, property_class):
        return self.properties.get(property_class.key(), None)

    def __add_property(self, property):
        self.properties[property.key()] = property

    def __remove_property(self, property):
        del self.properties[property.key()]
        property.destroy()
        property.thing = None

    def set_meta_property(self, meta_property_name, meta_property):
        existing_meta_property = getattr(self, meta_property_name)
        if existing_meta_property is not None:
            for prop in existing_meta_property.properties:
                self.unbecome(prop)

        if meta_property:
            for prop in meta_property.properties:
                self.become(prop)
        setattr(self, meta_property_name, meta_property)

    def set_form(self, form):
        self.set_meta_property('form', form)

    def set_material(self, material):
        self.set_meta_property('material', material)

    def is_property(self, property_class):
        return bool(self.__get_property(property_class))

    def get_property(self, property_class):
        return self.__get_property(property_class)

    def become(self, *property_classes, **kwargs):
        custom_description = kwargs.pop('custom_description', None)
        for property_class in property_classes:
            prop = self.__get_property(property_class)
            if prop:
                prop.count += 1
            else:
                prop = property_class(self)
                if custom_description:
                    prop.description = custom_description
                prop.count += 1
                self.__add_property(prop)

    def unbecome(self, property_class, force=False):
        prop = self.__get_property(property_class)
        if prop:
            if force:
                prop.count = 0
            else:
                prop.count -= 1

            if prop.count == 0:
                self.__remove_property(prop)

    def transfer_properties(self, from_thing, properties):
        """ Transfers the properties into this thing. For i.e. when a powder dissolves into a liquid """
        # Remove the properties from the old object
        from_thing.properties = dict([
            (k, v) for k, v in from_thing.properties.items()
            if v not in properties
        ])

        for prop in properties:
            if prop.key() not in self.properties.keys():
                self.properties[prop.key()] = prop
                prop.thing = self

    def remove_properties_of_types(self, types):
        self.properties = dict([
            (key, value) for (key, value) in self.properties.items()
            if not set(value.types).intersection(types)
        ])

    def get_properties_of_types(self, types):
        return [
            p for p in self.properties.values() if set(p.types).intersection(types)
        ]

    def has_properties(self, properties):
        return all(map(lambda x: self.is_property(x), properties))

    @property
    def location_properties(self):
        return [p for p in self.properties.values() if isinstance(p, LocationProperty)]

    @property
    def locations(self):
        output = []
        for prop in self.location_properties:
            output.extend(prop.locations.values())
        return output

from properties.location_properties import LocationProperty


def destroy_thing(thing):
    thing.destroyed = True
    for prop in thing.properties.values():
        prop.destroy()
    thing.properties = {}
    thing.form = None
    thing.material = None
    thing.location.remove_thing(thing)


class Thing(object):
    class Size(object):
        non_physical = -1000
        seed = 0  # The size of an apple seed
        apple = 1  # The size of an apple
        teapot = 2  # The size of a teapot
        dog = 3  # The size of a dog
        stool = 4  # The size of an ottoman
        person = 5  # The size of a human
        armoire = 6

        tiny = seed
        small = teapot
        medium = person
        large = armoire

        room = 1000

    def __init__(self):
        self.name = "A thing"
        self.icon = "?"
        self.properties = {}
        self.location = None
        self.form = None
        self.material = None
        self.size = Thing.Size.medium
        self.is_player = False
        self.destroyed = False

    def __repr__(self):
        return '<Thing:%s>' % self.name

    def tell(self, message):
        if self.is_player:
            print message

    def tell_room(self, message):
        for thing in self.location.things:
            if thing != self:
                thing.tell(message)

    def send_message(self, message_type, *args, **kwargs):
        for prop in self.properties.values():
            prop.receive_message(message_type, *args, **kwargs)

    def __get_property(self, property_class):
        return self.properties.get(str(property_class), None)

    def __add_property(self, property):
        self.properties[str(property.__class__)] = property

    def __remove_property(self, property):
        del self.properties[str(property.__class__)]
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

    def become(self, property_class):
        prop = self.__get_property(property_class)
        if prop:
            prop.count += 1
        else:
            prop = property_class(self)
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

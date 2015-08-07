from enums import Size


class Location(object):
    def __init__(self):
        self.things = []
        self._name = 'Nowhere in particular'
        # Static exits for rooms
        self.exits = []
        self._size = Size.room

    def __repr__(self):
        return '<Location:"%s">' % self.name

    @property
    def size(self):
        return self._size

    def can_contain(self, thing):
        return True

    def add_thing(self, thing):
        if thing.location is not None:
            thing.location.things.remove(thing)

        if object not in self.things:
            self.things.append(thing)
        thing.location = self

    def tell(self, message):
        for thing in self.things:
            thing.tell(message)

    def remove_thing(self, thing):
        """
        Should only be called when an object is destroyed,
        otherwise use add_thing to maintain thing location consistency
        """
        self.things.remove(thing)

    def get_all_exits(self):
        """ Static and property exits """
        result = []
        result.extend(self.exits)
        for thing in self.things:
            for lp in thing.location_properties:
                result.extend(lp.entrances)
        return result

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value


class PropertyLocation(Location):
    """ For locations implanted within properties """
    def __init__(self, prop):
        super(PropertyLocation, self).__init__()
        self.prop = prop

    def can_contain(self, thing):
        return thing.size <= self.size and thing != self.thing

    @property
    def size(self):
        return self.thing.size

    @property
    def thing(self):
        return self.prop.thing

    @property
    def name(self):
        return self.name_template % {
            'thing_name': self.thing.name,
            'prop': self.prop
        }


class Exit(object):
    def __init__(self):
        self.description_template = 'To %(to_location)s'

    @property
    def description(self):
        return self.description_template % self._get_description_parameters()

    def _get_description_parameters(self):
        return {
            'to_location': self.to_location.name
        }

    def can_traverse(self, thing):
        return True

    def can_access(self, thing):
        """
        Used for i.e. reaching into containers and pulling things out
        without actually entering them
        """
        return False

    def can_view(self, thing):
        """ Can <thing> see through this and receive messages from those inside? """
        return False

    @property
    def from_location(self):
        raise NotImplementedError()

    @property
    def to_location(self):
        raise NotImplementedError()


class StaticExit(Exit):
    """ Exits with a static exit location, i.e. built in room exits """

    def __init__(self, from_loc, to_loc):
        super(StaticExit, self).__init__()
        self._from_loc = from_loc
        self._to_loc = to_loc
        self.description_template = 'To %(to_location)s'

    @property
    def from_location(self):
        return self._from_loc

    @property
    def to_location(self):
        return self._to_loc


class ThingExit(Exit):
    def __init__(self, thing, access_requirements=None, visible_requirements=None):
        super(ThingExit, self).__init__()
        self._thing = thing
        self._access_requirements = access_requirements or []
        self._visible_requirements = visible_requirements or []

    def _get_description_parameters(self):
        d = super(ThingExit, self)._get_description_parameters()
        d.update({'thing': self._thing.name})
        return d

    def can_access(self, thing):
        return all(map(lambda x: self._thing.is_property(x), self._access_requirements))

    def can_view(self, thing):
        return all(map(lambda x: self._thing.is_property(x), self._visible_requirements))

    def can_traverse(self, thing):
        return thing.size <= self._thing.size


class OutsideExit(ThingExit):
    """ Exits to outside the given thing """

    def __init__(self, from_loc, thing, *args, **kwargs):
        super(OutsideExit, self).__init__(thing, *args, **kwargs)
        self._from_location = from_loc
        self.description_template = 'Out of %(thing)s'

    @property
    def to_location(self):
        return self._thing.location

    @property
    def from_location(self):
        return self._from_location


class EntranceExit(ThingExit):
    """ Entrance into a particular thing """
    def __init__(self, thing, to_loc, *args, **kwargs):
        super(EntranceExit, self).__init__(thing, *args, **kwargs)
        self._to_location = to_loc
        self.description_template = 'Into %(thing)s'

    @property
    def to_location(self):
        return self._to_location

    @property
    def from_location(self):
        return self._thing.location
